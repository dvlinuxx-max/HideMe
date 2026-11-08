import sys, os, argparse, json, re

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

API = "https://i.instagram.com/api/v1/"
SET_URL = API + "settings/set_bool/"
GET_URL = API + "settings/get_bool/"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".hide_state.json")

ALIASES = {
    "followers": "hide_followers_following_list",
    "account": "hide_self_from_others_lists",
}

DESC = {
    "followers": "Hide your followers and following lists from your profile",
    "account": "Hide your account from other people's lists",
}


def clean_sessionid(raw):
    if not raw:
        return ""
    raw = raw.strip().strip('"').strip("'").strip()
    m = re.search(r'sessionid\s*=\s*([^;,"\s]+)', raw)
    if m:
        raw = m.group(1)
    return raw.strip()


def ask_sessionid():
    print("\nPaste your sessionid cookie and press Enter:")
    print("(Chrome: F12 > Application > Cookies > instagram.com > sessionid)")
    try:
        return clean_sessionid(input("sessionid> "))
    except EOFError:
        return ""


def resolve_sessionid(arg):
    sid = clean_sessionid(arg) or clean_sessionid(os.environ.get("IG_SESSIONID", "")) or ask_sessionid()
    if not sid or ("%3A" not in sid and ":" not in sid):
        print("\nInvalid sessionid cookie.")
        sys.exit(2)
    return sid


def load_cache():
    try:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(setting_id, value_bool):
    d = load_cache()
    d[setting_id] = value_bool
    try:
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass


def login(sessionid):
    from instagrapi import Client
    cl = Client()
    print("\nLogging in...")
    cl.login_by_sessionid(sessionid)
    print("Logged in as @%s (pk=%s)" % (cl.username, cl.user_id))
    return cl


def session_headers(cl):
    h = dict(cl.private.headers)
    h["Content-Type"] = "application/x-www-form-urlencoded"
    return h


def do_set(cl, setting_id, value_bool):
    body = "setting_id=%s&value=%s" % (setting_id, "true" if value_bool else "false")
    r = cl.private.post(SET_URL, data=body, headers=session_headers(cl), timeout=30)
    print("\nHTTP %s - %s" % (r.status_code, r.text[:400]))
    ok = False
    try:
        ok = r.json().get("status") == "ok"
    except Exception:
        pass
    if ok:
        save_cache(setting_id, value_bool)
    print("Result:", "done (status=ok)" if ok else "failed - may be restricted for your account")
    return ok


def read_one(cl, setting_id):
    try:
        r = cl.private.get(GET_URL, params={"setting_id": setting_id},
                           headers=session_headers(cl), timeout=30)
        if r.status_code == 200:
            j = r.json()
            if "value" in j:
                return ("server", bool(j["value"]))
    except Exception:
        pass
    c = load_cache()
    if setting_id in c:
        return ("local", bool(c[setting_id]))
    return ("unknown", None)


def do_status(cl):
    print("\nSettings status:")
    for alias, setting_id in ALIASES.items():
        src, val = read_one(cl, setting_id)
        state = "ON" if val is True else ("OFF" if val is False else "UNKNOWN")
        note = {"server": "(from server)", "local": "(last local value)",
                "unknown": "(could not read)"}[src]
        print("  [%s] %-10s %s" % (state, alias, note))


def main():
    ap = argparse.ArgumentParser(description="Hide your Instagram followers and following lists.")
    ap.add_argument("--setting", default="followers", choices=list(ALIASES))
    ap.add_argument("--value", choices=["on", "off"])
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--sessionid", default="")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()

    if not a.status and not a.value:
        ap.error("use --value on/off or --status")

    if a.status:
        cl = login(resolve_sessionid(a.sessionid))
        do_status(cl)
        return

    setting_id = ALIASES[a.setting]
    val_bool = (a.value == "on")
    print("Setting : %s (%s)" % (a.setting, DESC[a.setting]))
    print("Value   : %s" % ("on" if val_bool else "off"))
    print("Request : POST %s" % SET_URL)
    print("Body    : setting_id=%s&value=%s" % (setting_id, "true" if val_bool else "false"))
    if not a.yes:
        print("\nDry run. Add --yes to actually send (it will ask for the cookie).")
        return
    cl = login(resolve_sessionid(a.sessionid))
    do_set(cl, setting_id, val_bool)


if __name__ == "__main__":
    main()
