import cx_Oracle
import pyotp
import secrets
import pandas as pd
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------------------
# DB
# --------------------------------
def get_conn():
    return cx_Oracle.connect("APP_USER/PASSWORD@HOST:1521/ORCLPDB1")


# --------------------------------
# PASSWORDS
# --------------------------------
def hash_password(p):
    return pwd.hash(p)

def verify_password(p, h):
    return pwd.verify(p, h)


# --------------------------------
# USERS
# --------------------------------
def create_user(username, email, password, name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO app_users(username,email,full_name)
        VALUES(:1,:2,:3)
        RETURNING user_id INTO :4
    """, [username,email,name, cur.var(cx_Oracle.NUMBER)])

    uid = int(cur.getvalue(4)[0])

    cur.execute("""
        INSERT INTO password_history(user_id,password_hash,reason)
        VALUES(:1,:2,'initial')
    """, [uid, hash_password(password)])

    cur.execute("INSERT INTO user_mfa(user_id) VALUES(:1)", [uid])

    conn.commit()
    conn.close()
    return uid


def activate_user(uid):
    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        UPDATE app_users SET is_active=1 WHERE user_id=:1
    """,[uid])

    cur.execute("""
        INSERT INTO audit_logs(target_user_id,action)
        VALUES(:1,'activate_user')
    """,[uid])

    conn.commit()
    conn.close()


# --------------------------------
# MFA
# --------------------------------
def enable_mfa(uid):
    secret = pyotp.random_base32()

    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        UPDATE user_mfa SET totp_secret=:1,enabled=1
        WHERE user_id=:2
    """,[secret,uid])

    conn.commit()
    conn.close()
    return secret


def verify_mfa(uid, token):
    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        SELECT totp_secret FROM user_mfa
        WHERE user_id=:1 AND enabled=1
    """,[uid])

    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    secret = row[0]
    return pyotp.TOTP(secret).verify(token, valid_window=1)


# --------------------------------
# LOGIN
# --------------------------------
def record_login(uid, user, ok, reason, ip, agent):
    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO login_attempts
        (user_id,username,success,reason,ip_address,user_agent)
        VALUES(:1,:2,:3,:4,:5,:6)
    """,[uid,user,int(ok),reason,ip,agent])

    conn.commit()
    conn.close()


def create_session(uid, ip, agent):
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(days=7)

    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO user_sessions
        (user_id,session_token,ip_address,user_agent,expires_at)
        VALUES(:1,:2,:3,:4,:5)
    """,[uid,token,ip,agent,expiry])

    conn.commit()
    conn.close()
    return token


def login(username, password, ip, agent):

    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        SELECT u.user_id,p.password_hash,NVL(m.enabled,0)
        FROM app_users u
        JOIN password_history p ON u.user_id=p.user_id
        LEFT JOIN user_mfa m ON u.user_id=m.user_id
        WHERE u.username=:1
        ORDER BY p.created_at DESC FETCH FIRST 1 ROW ONLY
    """,[username])

    row = cur.fetchone()
    conn.close()

    if not row:
        record_login(None,username,0,"NO_USER",ip,agent)
        return "NO_USER"

    uid, hsh, mfa = row

    if not verify_password(password,hsh):
        record_login(uid,username,0,"BAD_PASSWORD",ip,agent)
        return "BAD_PASSWORD"

    if mfa:
        record_login(uid,username,0,"MFA_REQUIRED",ip,agent)
        return f"MFA_REQUIRED:{uid}"

    token = create_session(uid,ip,agent)
    record_login(uid,username,1,"LOGIN_OK",ip,agent)
    return token


# --------------------------------
# ACTIVITY
# --------------------------------
def log_activity(uid, action, meta=""):
    conn=get_conn()
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO user_activity(user_id,action,metadata)
        VALUES(:1,:2,:3)
    """,[uid,action,meta])

    conn.commit()
    conn.close()


# --------------------------------
# REPORTING
# --------------------------------
def report_users():
    conn=get_conn()
    df=pd.read_sql("""
        SELECT username,email,is_active,is_locked,created_at
        FROM app_users
    """,conn)
    conn.close()
    return df


def report_logins():
    conn=get_conn()
    df=pd.read_sql("""
        SELECT username,success,reason,ip_address,created_at
        FROM login_attempts
        ORDER BY created_at DESC
    """,conn)
    conn.close()
    return df
