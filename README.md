# HideMe

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)

A command-line tool to hide your Instagram followers and following lists from other people.

Keywords: instagram, hide followers, hide following list, instagram privacy, followers
list, instagram api, instagrapi, privacy tool, cli.

It runs locally in your terminal. You provide your own Instagram session cookie, and the
request is sent to Instagram directly from your machine. The cookie is never uploaded
anywhere else.

## What it does

Two short options, each turns an account privacy setting on or off:

- `followers` — other people can no longer see your followers or following list on your
  profile.
- `account` — your account stops appearing inside other people's follower and following
  lists.

## How it works

Instagram's mobile app has a server-side settings endpoint:

```
POST https://i.instagram.com/api/v1/settings/set_bool/
setting_id=<id>&value=true|false
```

The tool signs in with your session cookie and sends that request. The change is stored on
Instagram's servers, so it applies for everyone, not just on your own screen.

## Requirements

- Python 3.10+
- [instagrapi](https://pypi.org/project/instagrapi/)

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# hide your followers / following list
python hideme.py --value on --yes

# show it again
python hideme.py --value off --yes

# hide your account from other people's lists
python hideme.py --setting account --value on --yes

# read the current state of both settings
python hideme.py --status
```

`followers` is the default option, so you only pass `--setting account` for the second one.
You can pass the cookie with `--sessionid "..."` or the `IG_SESSIONID` environment variable;
otherwise the tool asks for it. Running without `--yes` is a dry run that prints the request
without sending it.

## Getting your session cookie

1. Open `instagram.com` in Chrome and log in.
2. Press `F12`, open the **Application** tab, then **Cookies** → `https://www.instagram.com`.
3. Copy the value of the `sessionid` cookie.

Your cookie is your account key. Keep it private and do not share it.

## Notes

- This uses Instagram's private (undocumented) API, which is against Instagram's Terms of
  Service. Use it on your own account and at your own risk.
- Some accounts may not have these settings available. In that case the request returns an
  error, which is expected.
- This project is not affiliated with, endorsed by, or connected to Instagram or Meta.

## License

MIT. See [LICENSE](LICENSE).
