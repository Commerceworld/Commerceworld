import json
import os
import hashlib
import secrets
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_FILE = 'data.json'
AUTH_FILE = 'auth.json'

valid_tokens = set()

# ── Data helpers ──────────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        default = {
            "config": {
                "name": "CommerceWorld",
                "tagline": "Your trusted source for digital commerce news.",
                "copyright": "© 2026 CommerceWorld. All rights reserved.",
                "nlTitle": "Stay in the loop",
                "nlSub": "Get the latest commerce news delivered to your inbox."
            },
            "articles": [],
            "footerLinks": {"company": [], "resources": [], "social": []}
        }
        save_data(default)
        return default
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_auth():
    if not os.path.exists(AUTH_FILE):
        h = hashlib.sha256('admin'.encode()).hexdigest()
        auth = {'password_hash': h}
        with open(AUTH_FILE, 'w') as f:
            json.dump(auth, f)
        return auth
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)

def save_auth(auth):
    with open(AUTH_FILE, 'w') as f:
        json.dump(auth, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def check_token():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return False
    return auth[7:] in valid_tokens

# ── HTML (entire frontend) ────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CommerceWorld</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{
  --gold:#F5C518;--gold-d:#C9A000;
  --bg:#0F1117;--bg2:#181B28;--bg3:#22253A;
  --text:#FFFFFF;--text2:#B0B3C1;--text3:#5A5E72;
  --border:#252840;--card:#181B28;
  --red:#E53E3E;--green:#38A169;--blue:#4299E1;--purple:#805AD5;--orange:#DD6B20;
}
[data-theme=light]{
  --bg:#F4F6FF;--bg2:#FFFFFF;--bg3:#ECEEF8;
  --text:#0A0C18;--text2:#3A3D52;--text3:#8A8DA3;
  --border:#DDE0EE;--card:#FFFFFF;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;transition:background .3s,color .3s;overflow-x:hidden}
.view{display:none}.view.active{display:block}

/* NAV */
nav.topnav{
  position:sticky;top:0;z-index:200;
  background:var(--bg2);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 14px;height:58px;gap:10px;
}
.nav-logo{flex:1;font-size:1.2rem;font-weight:900;color:var(--text);cursor:pointer}
.nav-logo span{color:var(--gold)}
.nav-btn{background:none;border:none;cursor:pointer;color:var(--text);padding:7px;border-radius:6px;display:flex;align-items:center;transition:background .2s}
.nav-btn:hover{background:var(--bg3)}
.admin-btn{
  background:linear-gradient(135deg,#1a1d2e,#252840);
  border:1px solid var(--border);color:var(--text3);
  padding:6px 12px;border-radius:6px;font-size:0.75rem;
  font-weight:700;cursor:pointer;letter-spacing:.5px;
  display:flex;align-items:center;gap:5px;transition:all .2s;
}
.admin-btn:hover{border-color:var(--gold);color:var(--gold)}
.admin-btn.active-admin{border-color:var(--gold);color:var(--gold);background:rgba(245,197,24,.07)}

/* FLOATING CATS */
.float-cats{
  position:sticky;top:58px;z-index:190;
  background:var(--bg2);border-bottom:1px solid var(--border);
  display:flex;overflow-x:auto;gap:0;padding:0 14px;scrollbar-width:none;
}
.float-cats::-webkit-scrollbar{display:none}
.cat-tab{
  padding:11px 14px;font-size:0.75rem;font-weight:700;
  letter-spacing:.6px;text-transform:uppercase;
  color:var(--text3);border:none;background:none;
  cursor:pointer;border-bottom:2px solid transparent;
  white-space:nowrap;transition:all .2s;
}
.cat-tab.active{color:var(--gold);border-bottom-color:var(--gold)}
.cat-tab:hover{color:var(--text)}

/* SEARCH */
.search-wrap{max-width:760px;margin:14px auto 0;padding:0 14px}
.search-bar{display:flex}
.search-bar input{
  flex:1;padding:10px 14px;
  background:var(--bg3);border:1px solid var(--border);
  border-right:none;border-radius:6px 0 0 6px;
  color:var(--text);font-size:0.88rem;outline:none;
}
.search-bar input::placeholder{color:var(--text3)}
.search-bar button{padding:10px 18px;background:var(--gold);border:none;border-radius:0 6px 6px 0;font-weight:700;font-size:0.85rem;cursor:pointer;color:#000}

/* FEED */
.feed-wrap{max-width:760px;margin:0 auto;padding:18px 14px}
.section-label{display:flex;align-items:center;gap:10px;font-size:.85rem;font-weight:800;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px}
.section-label::before{content:'';width:3px;height:18px;background:var(--gold);border-radius:2px}
.thumb-row{display:flex;gap:10px;overflow-x:auto;margin-bottom:24px;scrollbar-width:none}
.thumb-row::-webkit-scrollbar{display:none}
.thumb-card{flex:0 0 138px;cursor:pointer;color:var(--text)}
.thumb-card img{width:138px;height:86px;object-fit:cover;border-radius:6px;display:block;transition:opacity .2s}
.thumb-card:hover img{opacity:.82}
.thumb-title{font-size:.74rem;font-weight:600;margin-top:5px;line-height:1.3}

/* ARTICLE CARD */
.article-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;overflow:hidden;margin-bottom:18px;
  cursor:pointer;transition:border-color .2s,transform .15s;
  display:block;text-decoration:none;color:var(--text);position:relative;
}
.article-card:hover{border-color:var(--gold);transform:translateY(-1px)}
.article-card img{width:100%;height:195px;object-fit:cover;display:block}
.a-body{padding:13px}
.a-meta{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.tag{padding:3px 7px;border-radius:4px;font-size:.68rem;font-weight:700;letter-spacing:.4px;text-transform:uppercase}
.tag.trade{background:var(--gold);color:#000}.tag.tech{background:var(--blue);color:#fff}
.tag.web3{background:var(--purple);color:#fff}.tag.currency{background:var(--green);color:#fff}
.tag.startups{background:var(--red);color:#fff}.tag.trend{background:var(--orange);color:#fff}
.tag.latest{background:var(--gold);color:#000}
.a-date{font-size:.72rem;color:var(--text3)}
.a-title{font-size:1rem;font-weight:700;line-height:1.4;margin-bottom:6px}
.a-excerpt{font-size:.83rem;color:var(--text2);line-height:1.6}
.read-more{display:inline-flex;align-items:center;gap:4px;margin-top:9px;font-size:.78rem;font-weight:700;color:var(--gold)}
.save-btn{
  position:absolute;top:10px;right:10px;
  background:rgba(0,0,0,.55);border:none;border-radius:50%;
  width:32px;height:32px;display:flex;align-items:center;justify-content:center;
  cursor:pointer;color:#fff;transition:background .2s;backdrop-filter:blur(4px);
}
.save-btn:hover{background:rgba(245,197,24,.8);color:#000}
.save-btn.saved{background:var(--gold);color:#000}

/* PAGINATION */
.pagination{display:flex;align-items:center;justify-content:center;gap:8px;margin:24px 0}
.page-btn{padding:8px 16px;border:1px solid var(--border);background:none;color:var(--text);border-radius:4px;font-size:.82rem;font-weight:600;cursor:pointer;transition:all .2s}
.page-btn:hover:not(:disabled){border-color:var(--gold);color:var(--gold)}
.page-btn:disabled{opacity:.3;cursor:default}
.page-info{font-size:.88rem;color:var(--text3)}

/* ARTICLE PAGE */
#articlePageView{background:var(--bg)}
.art-page-wrap{max-width:760px;margin:0 auto;padding:20px 14px}
.back-btn{display:inline-flex;align-items:center;gap:6px;color:var(--text3);font-size:.82rem;font-weight:600;cursor:pointer;margin-bottom:18px;border:none;background:none;padding:0;transition:color .2s}
.back-btn:hover{color:var(--gold)}
.art-hero{width:100%;max-height:320px;object-fit:cover;border-radius:10px;margin-bottom:18px;display:block}
.art-page-meta{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.art-page-title{font-size:1.5rem;font-weight:900;line-height:1.3;margin-bottom:16px}
.art-page-content{font-size:.94rem;color:var(--text2);line-height:1.8}
.art-page-content h1,.art-page-content h2,.art-page-content h3{color:var(--text);margin:18px 0 8px}
.art-page-content p{margin-bottom:12px}
.art-page-content img{max-width:100%;border-radius:8px;margin:10px 0}
.art-page-content a{color:var(--gold)}
.art-page-content blockquote{border-left:3px solid var(--gold);padding-left:12px;color:var(--text3);font-style:italic;margin:14px 0}
.art-page-divider{border:none;border-top:1px solid var(--border);margin:28px 0}
.similar-section-label{font-size:.8rem;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--text3);margin-bottom:14px}
.similar-grid{display:flex;flex-direction:column;gap:12px}
.similar-card{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px;cursor:pointer;text-decoration:none;color:var(--text);transition:border-color .2s}
.similar-card:hover{border-color:var(--gold)}
.similar-card img{width:80px;height:56px;object-fit:cover;border-radius:5px;flex-shrink:0}
.similar-card-body .a-title{font-size:.82rem;line-height:1.3;margin-bottom:3px}
.similar-card-body .a-date{font-size:.7rem}
.art-save-row{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.art-save-btn{
  display:flex;align-items:center;gap:6px;
  padding:7px 14px;border-radius:7px;border:1px solid var(--border);
  background:none;color:var(--text);font-size:.8rem;font-weight:600;cursor:pointer;transition:all .2s;
}
.art-save-btn:hover{border-color:var(--gold);color:var(--gold)}
.art-save-btn.saved{background:var(--gold);color:#000;border-color:var(--gold)}

/* NEWSLETTER */
.newsletter{background:var(--gold);padding:34px 20px;text-align:center;margin-top:10px}
.newsletter h2{font-size:1.35rem;font-weight:900;color:#000;letter-spacing:.8px;margin-bottom:7px}
.newsletter p{font-size:.88rem;color:#333;margin-bottom:14px}
.newsletter input{width:100%;padding:11px 13px;border-radius:6px;border:none;font-size:.88rem;margin-bottom:9px;outline:none;color:#222}
.newsletter button{width:100%;padding:12px;background:#000;color:#fff;border:none;border-radius:6px;font-weight:700;font-size:.88rem;letter-spacing:.8px;cursor:pointer;text-transform:uppercase}
.newsletter button:hover{background:#222}

/* FOOTER */
footer{background:#080A12;padding:34px 20px 18px}
.footer-inner{max-width:760px;margin:0 auto}
.footer-logo{font-size:1.25rem;font-weight:900;color:#fff;margin-bottom:7px}
.footer-logo span{color:var(--gold)}
.footer-desc{font-size:.8rem;color:#666;line-height:1.6;margin-bottom:26px}
.footer-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-bottom:26px}
.footer-col h4{font-size:.7rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--gold);margin-bottom:11px}
.footer-col a{display:block;color:#999;text-decoration:none;font-size:.85rem;margin-bottom:8px;transition:color .2s}
.footer-col a:hover{color:#fff}
.social-link{display:flex;align-items:center;gap:7px}
.footer-bottom{border-top:1px solid #1a1c2a;padding-top:14px;font-size:.72rem;color:#444;text-align:center}

/* OVERLAYS / MODALS */
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:500;align-items:flex-start;justify-content:center;overflow-y:auto;padding:20px 14px}
.overlay.open{display:flex}
.modal{background:var(--bg2);border-radius:12px;width:100%;max-width:700px;overflow:hidden;margin:auto}
.modal-hdr{display:flex;align-items:center;padding:14px 16px;border-bottom:1px solid var(--border);gap:10px}
.modal-hdr h2{flex:1;font-size:.95rem;font-weight:700}
.btn-close{background:none;border:none;cursor:pointer;color:var(--text3);font-size:1.3rem;padding:4px 8px;line-height:1}
.btn-close:hover{color:var(--text)}

/* ADMIN GATE */
.admin-gate{padding:32px 20px;text-align:center;max-width:340px;margin:0 auto}
.admin-gate h3{font-size:1rem;font-weight:800;margin-bottom:6px}
.admin-gate p{font-size:.8rem;color:var(--text3);margin-bottom:18px}
.gate-input{width:100%;padding:11px 14px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;color:var(--text);font-size:.9rem;outline:none;margin-bottom:10px;text-align:center;letter-spacing:2px}
.btn-gold{width:100%;padding:11px;background:var(--gold);color:#000;border:none;border-radius:7px;font-weight:700;font-size:.9rem;cursor:pointer}
.btn-gold:hover{background:var(--gold-d)}
.gate-err{color:var(--red);font-size:.78rem;margin-top:6px}

/* ADMIN PANEL */
.admin-tabs{display:flex;gap:0;border-bottom:1px solid var(--border);overflow-x:auto;scrollbar-width:none}
.admin-tabs::-webkit-scrollbar{display:none}
.adm-tab{padding:12px 16px;font-size:.78rem;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--text3);border:none;background:none;cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;transition:all .2s}
.adm-tab.active{color:var(--gold);border-bottom-color:var(--gold)}
.adm-panel{display:none;padding:18px 16px}
.adm-panel.active{display:block}
.adm-panel label{display:block;font-size:.78rem;font-weight:600;color:var(--text2);margin-bottom:5px;margin-top:12px}
.adm-panel label:first-child{margin-top:0}
.adm-input{width:100%;padding:9px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;color:var(--text);font-size:.85rem;outline:none}
.adm-input:focus{border-color:var(--gold)}
.adm-textarea{width:100%;padding:9px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;color:var(--text);font-size:.85rem;outline:none;resize:vertical;min-height:80px;font-family:'Inter',sans-serif}
.adm-row{display:flex;gap:8px;margin-top:14px}
.btn-sm{padding:8px 16px;border-radius:7px;font-size:.8rem;font-weight:700;cursor:pointer;border:none}
.btn-sm.gold{background:var(--gold);color:#000}
.btn-sm.gray{background:var(--bg3);color:var(--text);border:1px solid var(--border)}
.btn-sm.red{background:var(--red);color:#fff}
.adm-section-title{font-size:.82rem;font-weight:700;color:var(--text2);margin-bottom:10px;margin-top:16px;text-transform:uppercase;letter-spacing:.5px}
.adm-section-title:first-child{margin-top:0}
.footer-link-row{display:flex;gap:8px;align-items:center;margin-bottom:8px}
.footer-link-row input{flex:1;padding:7px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.8rem;outline:none}
.footer-link-row input:focus{border-color:var(--gold)}
.footer-link-row button{padding:7px 10px;background:var(--red);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.8rem}
.add-link-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.add-link-row input{flex:1;min-width:100px;padding:7px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.8rem;outline:none}
.add-link-row button{padding:7px 12px;background:var(--gold);color:#000;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:.8rem}
.article-mgmt-row{display:flex;align-items:flex-start;gap:10px;padding:10px;background:var(--bg3);border-radius:8px;margin-bottom:8px}
.article-mgmt-row img{width:56px;height:40px;object-fit:cover;border-radius:5px;flex-shrink:0}
.article-mgmt-info{flex:1;min-width:0}
.article-mgmt-info .a-title{font-size:.8rem;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.article-mgmt-info .a-date{font-size:.7rem;color:var(--text3)}
.article-mgmt-row .adm-row{margin-top:6px}

/* EDITOR */
.editor-title-input{width:100%;padding:13px 16px;background:var(--bg3);border:none;border-bottom:1px solid var(--border);font-size:1rem;font-weight:700;color:var(--text);outline:none;font-family:'Inter',sans-serif}
.editor-title-input::placeholder{color:var(--text3)}
.toolbar{display:flex;flex-wrap:wrap;gap:2px;padding:7px 10px;border-bottom:1px solid var(--border);background:var(--bg3)}
.tb-btn{background:none;border:1px solid transparent;color:var(--text);padding:4px 8px;border-radius:4px;font-size:.76rem;cursor:pointer;font-weight:600;transition:all .15s;min-width:28px;text-align:center}
.tb-btn:hover{background:var(--border)}
.tb-sep{width:1px;background:var(--border);margin:3px 4px}
.tb-color{position:relative}
.tb-color input[type=color]{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
select.tb-select{background:var(--bg2);border:1px solid var(--border);color:var(--text);padding:4px 6px;border-radius:4px;font-size:.74rem;cursor:pointer;outline:none}
.insert-panel{display:none;padding:11px 14px;border-top:1px solid var(--border);background:var(--bg3);gap:7px;flex-direction:column}
.insert-panel.open{display:flex}
.insert-panel label{font-size:.76rem;color:var(--text2);font-weight:600}
.insert-panel input[type=text],.insert-panel input[type=url]{width:100%;padding:8px 11px;background:var(--bg2);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.82rem;outline:none}
.insert-row{display:flex;gap:7px;align-items:center;flex-wrap:wrap}
.btn-ins{padding:7px 12px;background:var(--gold);color:#000;border:none;border-radius:6px;font-weight:700;font-size:.76rem;cursor:pointer}
.btn-can{padding:7px 12px;background:var(--border);color:var(--text);border:none;border-radius:6px;font-weight:600;font-size:.76rem;cursor:pointer}
.editor-area{min-height:240px;padding:13px 15px;color:var(--text);font-family:'Inter',sans-serif;font-size:.92rem;line-height:1.75;outline:none;overflow-y:auto}
.editor-area:empty::before{content:'Write your article here...';color:var(--text3);pointer-events:none}
.editor-area img{max-width:100%;border-radius:7px;margin:8px 0}
.editor-area a{color:var(--gold)}
.editor-area blockquote{border-left:3px solid var(--gold);padding-left:12px;color:var(--text2);font-style:italic;margin:12px 0}
.meta-fields{padding:11px 15px;border-top:1px solid var(--border);display:flex;gap:9px;flex-wrap:wrap}
.meta-fields select,.meta-fields input{padding:7px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:.8rem;outline:none;flex:1;min-width:110px}
.editor-footer{padding:11px 15px;border-top:1px solid var(--border);display:flex;gap:9px;justify-content:flex-end}
.btn-publish{padding:9px 22px;background:var(--gold);color:#000;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:.88rem}
.btn-draft-btn{padding:9px 16px;background:var(--bg3);color:var(--text);border:1px solid var(--border);border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem}

/* CUSTOMIZE */
.color-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.color-row label{font-size:.8rem;color:var(--text2);flex:1}
.color-row input[type=color]{width:36px;height:28px;border:1px solid var(--border);border-radius:4px;cursor:pointer;background:none;padding:2px}
.font-preview{font-size:.82rem;color:var(--text2);padding:8px 12px;background:var(--bg3);border-radius:6px;margin-top:8px;line-height:1.6}

/* DRAWER */
.scrim{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:300}
.scrim.open{display:block}
.drawer{
  display:none;position:fixed;top:0;left:0;bottom:0;width:78%;max-width:300px;
  background:var(--bg2);border-right:1px solid var(--border);z-index:310;
  flex-direction:column;overflow-y:auto;
}
.drawer.open{display:flex}
.drawer-header{
  padding:18px 16px 14px;
  border-bottom:1px solid var(--border);
  background:linear-gradient(135deg,var(--bg3),var(--bg2));
}
.drawer-top-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.drawer-logo{font-size:1.1rem;font-weight:900;color:var(--text)}
.drawer-logo span{color:var(--gold)}
.drawer-close-btn{background:none;border:none;color:var(--text3);font-size:1.2rem;cursor:pointer;padding:4px}
.user-profile{display:flex;align-items:center;gap:11px}
.user-avatar{
  width:42px;height:42px;border-radius:50%;
  background:linear-gradient(135deg,var(--gold),var(--gold-d));
  display:flex;align-items:center;justify-content:center;
  font-size:1.1rem;font-weight:900;color:#000;flex-shrink:0;
}
.user-info{flex:1;min-width:0}
.user-name{font-size:.88rem;font-weight:700;color:var(--text)}
.user-status{font-size:.72rem;color:var(--text3);margin-top:2px}
.user-stats{display:flex;gap:14px;margin-top:12px}
.user-stat{text-align:center}
.user-stat-num{font-size:.9rem;font-weight:800;color:var(--gold)}
.user-stat-lbl{font-size:.65rem;color:var(--text3);margin-top:1px}
.drawer-nav{padding:10px 0}
.drawer-nav-label{font-size:.64rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--text3);padding:10px 16px 4px}
.drawer-item{
  display:flex;align-items:center;gap:11px;
  padding:11px 16px;color:var(--text);text-decoration:none;
  font-size:.88rem;font-weight:600;cursor:pointer;border:none;background:none;
  width:100%;text-align:left;transition:background .15s;
}
.drawer-item:hover{background:var(--bg3);color:var(--gold)}
.drawer-item svg{flex-shrink:0;opacity:.7}
.drawer-item:hover svg{opacity:1}
.drawer-item .badge{
  margin-left:auto;background:var(--gold);color:#000;
  font-size:.62rem;font-weight:800;padding:2px 7px;border-radius:10px;
}
.drawer-divider{border:none;border-top:1px solid var(--border);margin:4px 0}
.drawer-sub{display:none;padding:0 16px 10px;}
.drawer-sub.open{display:block}
.drawer-sub-title{font-size:.7rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--text3);margin-bottom:8px;margin-top:4px}
.drawer-mini-card{
  display:flex;gap:9px;align-items:center;
  padding:8px;background:var(--bg3);border-radius:7px;
  margin-bottom:6px;cursor:pointer;transition:background .15s;border:1px solid transparent;
}
.drawer-mini-card:hover{border-color:var(--gold)}
.drawer-mini-card img{width:44px;height:32px;object-fit:cover;border-radius:4px;flex-shrink:0}
.drawer-mini-card-body{flex:1;min-width:0}
.drawer-mini-title{font-size:.76rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text)}
.drawer-mini-meta{font-size:.65rem;color:var(--text3);margin-top:2px}
.drawer-empty{font-size:.78rem;color:var(--text3);text-align:center;padding:14px 0;font-style:italic}
.drawer-clear-btn{font-size:.72rem;color:var(--red);background:none;border:none;cursor:pointer;padding:4px 0;display:block;margin:4px auto 0}
.drawer-logout{margin-top:auto;border-top:1px solid var(--border);padding:10px 0;}
.drawer-logout-btn{
  display:flex;align-items:center;gap:11px;
  padding:12px 16px;color:var(--red);font-size:.88rem;font-weight:600;
  cursor:pointer;background:none;border:none;width:100%;text-align:left;transition:background .15s;
}
.drawer-logout-btn:hover{background:rgba(229,62,62,.08)}

/* TOAST */
.toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%);background:var(--gold);color:#000;padding:9px 18px;border-radius:8px;font-weight:700;font-size:.8rem;z-index:999;opacity:0;transition:opacity .3s;pointer-events:none;white-space:nowrap}
.toast.show{opacity:1}

/* ADMIN BADGE */
.admin-badge{position:fixed;bottom:18px;right:14px;z-index:400;background:var(--bg2);border:1px solid var(--gold);border-radius:10px;padding:7px 12px;display:none;flex-direction:column;gap:5px;box-shadow:0 4px 24px rgba(0,0,0,.5)}
.admin-badge.visible{display:flex}
.admin-badge-label{font-size:.64rem;font-weight:700;color:var(--gold);letter-spacing:.6px;text-transform:uppercase;margin-bottom:2px}
.admin-action{display:flex;align-items:center;gap:7px;background:none;border:none;color:var(--text);font-size:.8rem;font-weight:600;cursor:pointer;padding:5px 8px;border-radius:6px;transition:background .2s;text-align:left;width:100%}
.admin-action:hover{background:var(--bg3)}
.admin-action svg{flex-shrink:0}

@media(min-width:600px){
  .footer-grid{grid-template-columns:repeat(4,1fr)}
  .similar-grid{flex-direction:row;flex-wrap:wrap}
  .similar-card{flex:0 0 calc(50% - 6px)}
}
</style>
</head>
<body>

<!-- SCRIM -->
<div class="scrim" id="scrim" onclick="closeDrawer()"></div>

<!-- DRAWER -->
<div class="drawer" id="drawer">
  <div class="drawer-header">
    <div class="drawer-top-row">
      <div class="drawer-logo">Commerce<span>World</span></div>
      <button class="drawer-close-btn" onclick="closeDrawer()">&#x2715;</button>
    </div>
    <div class="user-profile">
      <div class="user-avatar" id="drawerAvatar">R</div>
      <div class="user-info">
        <div class="user-name" id="drawerUsername">Reader</div>
        <div class="user-status" id="drawerStatus">&#9679; Active now</div>
      </div>
    </div>
    <div class="user-stats">
      <div class="user-stat"><div class="user-stat-num" id="statRead">0</div><div class="user-stat-lbl">Read</div></div>
      <div class="user-stat"><div class="user-stat-num" id="statSaved">0</div><div class="user-stat-lbl">Saved</div></div>
      <div class="user-stat"><div class="user-stat-num" id="statHistory">0</div><div class="user-stat-lbl">History</div></div>
    </div>
  </div>
  <div class="drawer-nav">
    <div class="drawer-nav-label">Browse</div>
    <button class="drawer-item" onclick="filterCat('LATEST');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>Latest
    </button>
    <button class="drawer-item" onclick="filterCat('TREND');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>Trending
    </button>
    <button class="drawer-item" onclick="filterCat('TRADE');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>Trade
    </button>
    <button class="drawer-item" onclick="filterCat('TECH');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>Tech
    </button>
    <button class="drawer-item" onclick="filterCat('WEB3');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>Web3
    </button>
    <button class="drawer-item" onclick="filterCat('CURRENCY');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9.354a4 4 0 100 5.292"/></svg>Currency
    </button>
    <button class="drawer-item" onclick="filterCat('STARTUPS');closeDrawer()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Startups
    </button>
    <hr class="drawer-divider">
    <div class="drawer-nav-label">My Library</div>
    <button class="drawer-item" id="savedToggle" onclick="toggleDrawerSub('savedSub','savedToggle')">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>Saved Articles
      <span class="badge" id="savedBadge">0</span>
    </button>
    <div class="drawer-sub" id="savedSub">
      <div class="drawer-sub-title">Saved</div>
      <div id="savedList"></div>
    </div>
    <button class="drawer-item" id="historyToggle" onclick="toggleDrawerSub('historySub','historyToggle')">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Reading History
      <span class="badge" id="historyBadge">0</span>
    </button>
    <div class="drawer-sub" id="historySub">
      <div class="drawer-sub-title">Recently Read</div>
      <div id="historyList"></div>
      <button class="drawer-clear-btn" onclick="clearHistory()">Clear history</button>
    </div>
  </div>
  <div class="drawer-logout">
    <button class="drawer-logout-btn" onclick="closeDrawer();showToast('See you next time!')">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>Close
    </button>
  </div>
</div>

<!-- NAV -->
<nav class="topnav">
  <button class="nav-btn" onclick="openDrawer()">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
  </button>
  <div class="nav-logo" onclick="showView('homeView');render()">Commerce<span>World</span></div>
  <button class="nav-btn" id="themeBtn" onclick="toggleTheme()" title="Toggle theme">
    <svg id="moonIcon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:block"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
    <svg id="sunIcon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
  </button>
  <button class="admin-btn" id="adminNavBtn" onclick="openAdminGate()">
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
    <span id="adminBtnLabel">Admin</span>
  </button>
</nav>

<!-- CATS -->
<div class="float-cats">
  <button class="cat-tab active" onclick="filterCat('LATEST')">LATEST</button>
  <button class="cat-tab" onclick="filterCat('TREND')">TREND</button>
  <button class="cat-tab" onclick="filterCat('TRADE')">TRADE</button>
  <button class="cat-tab" onclick="filterCat('TECH')">TECH</button>
  <button class="cat-tab" onclick="filterCat('CURRENCY')">CURRENCY</button>
  <button class="cat-tab" onclick="filterCat('STARTUPS')">STARTUPS</button>
  <button class="cat-tab" onclick="filterCat('WEB3')">WEB3</button>
</div>

<!-- HOME VIEW -->
<div class="view active" id="homeView">
  <div class="search-wrap">
    <div class="search-bar">
      <input type="text" id="searchInput" placeholder="Search articles..." onkeydown="if(event.key==='Enter')doSearch()">
      <button onclick="doSearch()">Go</button>
    </div>
  </div>
  <div class="feed-wrap">
    <div class="section-label" id="sectionLabel">THIS WEEK</div>
    <div class="thumb-row" id="thumbRow"></div>
    <div id="articleList"></div>
    <div class="pagination">
      <button class="page-btn" id="prevBtn" onclick="changePage(-1)" disabled>PREV</button>
      <span class="page-info" id="pageInfo">1 / 1</span>
      <button class="page-btn" id="nextBtn" onclick="changePage(1)" disabled>NEXT</button>
    </div>
  </div>
  <div class="newsletter">
    <h2 id="nlTitle">STAY AHEAD OF THE CURVE</h2>
    <p id="nlSub">Get the latest commerce intelligence delivered to your inbox.</p>
    <input type="email" id="emailInput" placeholder="Your email address">
    <button onclick="subscribe()">SUBSCRIBE</button>
  </div>
  <footer>
    <div class="footer-inner">
      <div class="footer-logo">Commerce<span>World</span></div>
      <div class="footer-desc" id="footerDesc"></div>
      <div class="footer-grid" id="footerGrid"></div>
      <div class="footer-bottom" id="footerBottom"></div>
    </div>
  </footer>
</div>

<!-- ARTICLE PAGE VIEW -->
<div class="view" id="articlePageView">
  <div class="art-page-wrap">
    <button class="back-btn" onclick="showView('homeView');render()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>Back
    </button>
    <img class="art-hero" id="apHero" src="" alt="">
    <div class="art-page-meta" id="apMeta"></div>
    <h1 class="art-page-title" id="apTitle"></h1>
    <div class="art-save-row">
      <button class="art-save-btn" id="artSaveBtn" onclick="artToggleSave()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>Save Article
      </button>
      <button class="admin-action" id="editArticleBtn" style="display:none;border:1px solid var(--border);border-radius:7px;padding:7px 14px;font-size:.8rem" onclick="editArticle(currentArticleId)">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>Edit
      </button>
    </div>
    <div class="art-page-content" id="apContent"></div>
    <hr class="art-page-divider">
    <div class="similar-section-label">YOU MAY ALSO LIKE</div>
    <div class="similar-grid" id="similarGrid"></div>
  </div>
  <div class="newsletter">
    <h2 id="nlTitle2">STAY AHEAD OF THE CURVE</h2>
    <input type="email" id="emailInput2" placeholder="Your email address">
    <button onclick="subscribe2()">SUBSCRIBE</button>
  </div>
  <footer>
    <div class="footer-inner">
      <div class="footer-logo">Commerce<span>World</span></div>
      <div class="footer-desc" id="footerDesc2"></div>
      <div class="footer-grid" id="footerGrid2"></div>
      <div class="footer-bottom" id="footerBottom2"></div>
    </div>
  </footer>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<!-- ADMIN FLOATING BADGE -->
<div class="admin-badge" id="adminBadge">
  <div class="admin-badge-label">&#9889; Admin Mode</div>
  <button class="admin-action" onclick="openEditor()">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>New Article
  </button>
  <button class="admin-action" onclick="openAdminPanel('customize')">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>Customize
  </button>
  <button class="admin-action" onclick="openAdminPanel('articles')">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Articles
  </button>
  <button class="admin-action" onclick="openAdminPanel('footer')">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>Footer Links
  </button>
  <button class="admin-action" onclick="openAdminPanel('settings')">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>Settings / Password
  </button>
  <button class="admin-action" style="color:var(--red)" onclick="logoutAdmin()">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>Admin Logout
  </button>
</div>

<!-- ADMIN GATE -->
<div class="overlay" id="gateOverlay">
  <div class="modal" style="max-width:400px">
    <div class="modal-hdr">
      <h2>&#128272; Admin Access</h2>
      <button class="btn-close" onclick="closeOverlay('gateOverlay')">&#x2715;</button>
    </div>
    <div class="admin-gate">
      <h3>Enter Admin Password</h3>
      <p>Admin access is required to write articles and manage this site.</p>
      <input class="gate-input" type="password" id="pwInput" placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;" onkeydown="if(event.key==='Enter')checkPw()">
      <button class="btn-gold" onclick="checkPw()">Unlock Admin</button>
      <div class="gate-err" id="gateErr"></div>
    </div>
  </div>
</div>

<!-- ADMIN PANEL -->
<div class="overlay" id="adminOverlay">
  <div class="modal">
    <div class="modal-hdr">
      <h2>&#9889; Admin Panel</h2>
      <button class="btn-close" onclick="closeOverlay('adminOverlay')">&#x2715;</button>
    </div>
    <div class="admin-tabs">
      <button class="adm-tab active" onclick="switchAdmTab('customize')">Customize</button>
      <button class="adm-tab" onclick="switchAdmTab('articles')">Articles</button>
      <button class="adm-tab" onclick="switchAdmTab('footer')">Footer</button>
      <button class="adm-tab" onclick="switchAdmTab('settings')">Settings</button>
    </div>
    <!-- Customize -->
    <div class="adm-panel active" id="adm-customize">
      <label>Site Name</label><input class="adm-input" id="custSiteName" placeholder="CommerceWorld">
      <label>Tagline / About</label><textarea class="adm-textarea" id="custTagline" placeholder="Short description..."></textarea>
      <label>Copyright Text</label><input class="adm-input" id="custCopyright" placeholder="&#169; 2026 CommerceWorld">
      <label>Newsletter Title</label><input class="adm-input" id="custNlTitle" placeholder="Stay ahead...">
      <label>Newsletter Subtitle</label><input class="adm-input" id="custNlSub" placeholder="Get the latest...">
      <div class="adm-row">
        <button class="btn-sm gold" onclick="applyCustomize()">Save Changes</button>
        <button class="btn-sm gray" onclick="resetCustomize()">Reset Defaults</button>
      </div>
    </div>
    <!-- Articles -->
    <div class="adm-panel" id="adm-articles">
      <div class="adm-row"><button class="btn-sm gold" onclick="closeOverlay('adminOverlay');openEditor()">+ New Article</button></div>
      <div style="margin-top:14px" id="articleMgmtList"></div>
      <div class="adm-row" style="margin-top:18px;border-top:1px solid var(--border);padding-top:14px">
        <button class="btn-sm red" onclick="clearAllArticles()">Delete All Articles</button>
      </div>
    </div>
    <!-- Footer -->
    <div class="adm-panel" id="adm-footer">
      <div class="adm-section-title">Company Links</div>
      <div id="footerCompanyLinks"></div>
      <div class="add-link-row">
        <input type="text" id="newCompanyLabel" placeholder="Label">
        <input type="url" id="newCompanyUrl" placeholder="URL">
        <button onclick="addFooterLink('company')">Add</button>
      </div>
      <div class="adm-section-title">Resource Links</div>
      <div id="footerResourceLinks"></div>
      <div class="add-link-row">
        <input type="text" id="newResourcesLabel" placeholder="Label">
        <input type="url" id="newResourcesUrl" placeholder="URL">
        <button onclick="addFooterLink('resources')">Add</button>
      </div>
      <div class="adm-section-title">Social Links</div>
      <div id="footerSocialLinks"></div>
      <div class="add-link-row">
        <input type="text" id="newSocialLabel" placeholder="Label">
        <input type="url" id="newSocialUrl" placeholder="URL">
        <button onclick="addFooterLink('social')">Add</button>
      </div>
      <div class="adm-row"><button class="btn-sm gold" onclick="saveFooterLinks()">Save Footer Links</button></div>
    </div>
    <!-- Settings -->
    <div class="adm-panel" id="adm-settings">
      <div class="adm-section-title">Change Admin Password</div>
      <label>Current Password</label><input class="adm-input" type="password" id="curPw" placeholder="Current password">
      <label>New Password</label><input class="adm-input" type="password" id="newPw" placeholder="New password (min 4 chars)">
      <label>Confirm New Password</label><input class="adm-input" type="password" id="confirmPw" placeholder="Confirm new password">
      <div class="adm-row"><button class="btn-sm gold" onclick="changePassword()">Update Password</button></div>
      <div id="pwChangeMsg" style="font-size:.8rem;margin-top:8px"></div>
    </div>
  </div>
</div>

<!-- EDITOR -->
<div class="overlay" id="editorOverlay">
  <div class="modal">
    <div class="modal-hdr">
      <h2 id="editorModalTitle">New Article</h2>
      <button class="btn-close" onclick="closeOverlay('editorOverlay')">&#x2715;</button>
    </div>
    <input class="editor-title-input" type="text" id="articleTitleInput" placeholder="Article headline...">
    <div class="toolbar">
      <button class="tb-btn" onclick="execCmd('bold')" title="Bold"><b>B</b></button>
      <button class="tb-btn" onclick="execCmd('italic')" title="Italic"><i>I</i></button>
      <button class="tb-btn" onclick="execCmd('underline')" title="Underline"><u>U</u></button>
      <button class="tb-btn" onclick="execCmd('strikeThrough')" title="Strike"><s>S</s></button>
      <div class="tb-sep"></div>
      <select class="tb-select" onchange="execCmd('formatBlock',this.value);this.value=''">
        <option value="">Paragraph</option>
        <option value="h2">Heading 2</option>
        <option value="h3">Heading 3</option>
        <option value="blockquote">Quote</option>
        <option value="p">Normal</option>
      </select>
      <div class="tb-sep"></div>
      <button class="tb-btn" onclick="execCmd('insertUnorderedList')" title="Bullet list">&#8226;</button>
      <button class="tb-btn" onclick="execCmd('insertOrderedList')" title="Numbered list">1.</button>
      <button class="tb-btn" onclick="execCmd('justifyLeft')" title="Left">&#8676;</button>
      <button class="tb-btn" onclick="execCmd('justifyCenter')" title="Center">&#8677;</button>
      <div class="tb-sep"></div>
      <button class="tb-btn" onclick="insertLink()" title="Link">&#128279;</button>
      <button class="tb-btn" onclick="toggleInsertPanel()" title="Insert image">&#128247;</button>
      <div class="tb-sep"></div>
      <button class="tb-btn tb-color" title="Text color">A
        <input type="color" onchange="execCmd('foreColor',this.value)">
      </button>
      <button class="tb-btn" onclick="execCmd('removeFormat')" title="Clear format">&#x2715;</button>
    </div>
    <div class="insert-panel" id="insertPanel">
      <label>Insert image from URL</label>
      <div class="insert-row">
        <input type="url" id="imgUrl" placeholder="https://...">
        <button class="btn-ins" onclick="insertImageUrl()">Insert</button>
        <button class="btn-can" onclick="toggleInsertPanel()">Cancel</button>
      </div>
      <label>Or upload from device</label>
      <div class="insert-row">
        <input type="file" id="imgFile" accept="image/*" style="flex:1;font-size:.78rem">
        <button class="btn-ins" onclick="insertImageFile()">Upload</button>
      </div>
    </div>
    <div class="editor-area" id="editorArea" contenteditable="true"></div>
    <div class="meta-fields">
      <select id="catSelect">
        <option value="TRADE">TRADE</option>
        <option value="TECH">TECH</option>
        <option value="WEB3">WEB3</option>
        <option value="CURRENCY">CURRENCY</option>
        <option value="STARTUPS">STARTUPS</option>
        <option value="TREND">TREND</option>
      </select>
      <input type="text" id="excerptInput" placeholder="Short excerpt (optional)">
      <input type="url" id="coverInput" placeholder="Cover image URL (optional)">
    </div>
    <div class="editor-footer">
      <button class="btn-draft-btn" onclick="saveDraft()">Save Draft</button>
      <button class="btn-publish" onclick="publishArticle()">Publish</button>
    </div>
  </div>
</div>

<script>
const API_BASE = '';

let isAdmin = false;
let currentPage = 1;
let currentCat = 'LATEST';
let searchQuery = '';
let editingId = null;
let currentArticleId = null;
const PER_PAGE = 3;

let visitedIds = [];
let savedIds = [];
let historyLog = [];

const IMGS = [
  'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=700&q=80',
  'https://images.unsplash.com/photo-1497366216548-37526070297c?w=700&q=80',
  'https://images.unsplash.com/photo-1516245834210-c4c142787335?w=700&q=80',
  'https://images.unsplash.com/photo-1633158829799-96bb13e41e64?w=700&q=80',
  'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=700&q=80',
  'https://images.unsplash.com/photo-1551434678-e076c223a692?w=700&q=80',
];

let articles = [];
let footerLinks = { company: [], resources: [], social: [] };
let siteConfig = { name: 'CommerceWorld', tagline: '', copyright: '', nlTitle: '', nlSub: '' };

function adminToken() { return sessionStorage.getItem('cw_admin_token') || null; }
function authHeaders() { const t = adminToken(); return t ? { 'Authorization': 'Bearer ' + t } : {}; }

async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}
async function apiSend(method, path, body) {
  const res = await fetch(API_BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

async function loadFromServer() {
  try {
    const [cfg, arts, links] = await Promise.all([
      apiGet('/api/config'),
      apiGet('/api/articles'),
      apiGet('/api/footer-links'),
    ]);
    siteConfig = { ...siteConfig, ...cfg };
    articles = arts;
    footerLinks = links;
  } catch (e) {
    console.error('Could not reach backend:', e);
  }
  render();
}

/* USER LIBRARY */
function recordVisit(article) {
  visitedIds = visitedIds.filter(i => i !== article.id);
  visitedIds.unshift(article.id);
  if (visitedIds.length > 20) visitedIds = visitedIds.slice(0, 20);
  const ts = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
  historyLog = historyLog.filter(h => h.id !== article.id);
  historyLog.unshift({id: article.id, title: article.title, ts, date: article.date, img: article.img, cat: article.cat});
  if (historyLog.length > 50) historyLog = historyLog.slice(0, 50);
  updateLibraryUI();
}

function toggleSave(id) {
  if (savedIds.includes(id)) { savedIds = savedIds.filter(i => i !== id); return false; }
  savedIds.push(id); return true;
}

function clearHistory() {
  historyLog = []; visitedIds = []; updateLibraryUI(); showToast('History cleared');
}

function toggleDrawerSub(subId, btnId) {
  const sub = document.getElementById(subId);
  sub.classList.toggle('open');
}

function updateLibraryUI() {
  document.getElementById('statRead').textContent = visitedIds.length;
  document.getElementById('statSaved').textContent = savedIds.length;
  document.getElementById('statHistory').textContent = historyLog.length;
  document.getElementById('savedBadge').textContent = savedIds.length;
  document.getElementById('historyBadge').textContent = historyLog.length;

  const savedArts = savedIds.map(id => articles.find(a => a.id === id)).filter(Boolean);
  document.getElementById('savedList').innerHTML = savedArts.length
    ? savedArts.map(a => `<div class="drawer-mini-card" onclick="closeDrawer();openArticlePage(${a.id})">
        <img src="${a.img}" onerror="this.src='https://placehold.co/44x32?text=img'" alt="">
        <div class="drawer-mini-card-body"><div class="drawer-mini-title">${a.title}</div><div class="drawer-mini-meta">${a.cat} &bull; ${a.date}</div></div>
      </div>`).join('')
    : '<div class="drawer-empty">No saved articles yet.</div>';

  document.getElementById('historyList').innerHTML = historyLog.length
    ? historyLog.slice(0,10).map(h => `<div class="drawer-mini-card" onclick="closeDrawer();openArticlePage(${h.id})">
        <img src="${h.img}" onerror="this.src='https://placehold.co/44x32?text=img'" alt="">
        <div class="drawer-mini-card-body"><div class="drawer-mini-title">${h.title}</div><div class="drawer-mini-meta">${h.cat} &bull; ${h.ts}</div></div>
      </div>`).join('')
    : '<div class="drawer-empty">No reading history yet.</div>';
}

/* VIEWS */
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo({top: 0, behavior: 'smooth'});
  if (id === 'articlePageView') {
    document.getElementById('editArticleBtn').style.display = isAdmin ? 'flex' : 'none';
  }
}

/* RENDER */
function getFiltered() {
  let list = [...articles];
  if (searchQuery) { const q = searchQuery.toLowerCase(); list = list.filter(a => a.title.toLowerCase().includes(q) || (a.excerpt||'').toLowerCase().includes(q)); }
  if (currentCat !== 'LATEST') list = list.filter(a => a.cat === currentCat);
  return list.reverse();
}

function render() {
  document.title = siteConfig.name || 'CommerceWorld';
  document.querySelector('.nav-logo').innerHTML = (siteConfig.name || 'CommerceWorld').replace('World','<span>World</span>');
  renderFooter(); renderFooter2();

  const filtered = getFiltered();
  const total = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  if (currentPage > total) currentPage = total;
  const page = filtered.slice((currentPage-1)*PER_PAGE, currentPage*PER_PAGE);

  document.getElementById('sectionLabel').textContent = currentCat === 'LATEST' ? 'THIS WEEK' : currentCat;
  document.getElementById('prevBtn').disabled = currentPage <= 1;
  document.getElementById('nextBtn').disabled = currentPage >= total;
  document.getElementById('pageInfo').textContent = currentPage + ' / ' + total;

  const thumbs = filtered.slice(0, 8);
  document.getElementById('thumbRow').innerHTML = thumbs.map(a => `
    <div class="thumb-card" onclick="openArticlePage(${a.id})">
      <img src="${a.img}" alt="${a.title}" onerror="this.src='https://placehold.co/138x86?text=img'">
      <div class="thumb-title">${a.title}</div>
    </div>`).join('');

  document.getElementById('articleList').innerHTML = page.length
    ? page.map(a => {
        const isSaved = savedIds.includes(a.id);
        return `<div class="article-card" onclick="openArticlePage(${a.id})">
          <img src="${a.img}" alt="${a.title}" onerror="this.src='https://placehold.co/700x195?text=img'">
          <button class="save-btn ${isSaved?'saved':''}" onclick="event.stopPropagation();cardToggleSave(${a.id},this)" title="${isSaved?'Unsave':'Save'}">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="${isSaved?'currentColor':'none'}" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
          </button>
          <div class="a-body">
            <div class="a-meta"><span class="tag ${a.cat.toLowerCase()}">${a.cat}</span><span class="a-date">${a.date}</span></div>
            <div class="a-title">${a.title}</div>
            <div class="a-excerpt">${a.excerpt}</div>
            <span class="read-more">READ MORE &rarr;</span>
          </div>
        </div>`;}).join('')
    : '<p style="text-align:center;color:var(--text3);padding:40px 0">No articles found.</p>';

  document.getElementById('nlTitle').textContent = siteConfig.nlTitle;
  document.getElementById('nlSub').textContent = siteConfig.nlSub;
}

function cardToggleSave(id, btn) {
  const saved = toggleSave(id);
  btn.classList.toggle('saved', saved);
  btn.querySelector('svg').setAttribute('fill', saved ? 'currentColor' : 'none');
  btn.title = saved ? 'Unsave' : 'Save';
  showToast(saved ? 'Saved \u2713' : 'Removed from saved');
}

function changePage(dir) {
  const filtered = getFiltered();
  const total = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  currentPage = Math.max(1, Math.min(total, currentPage + dir));
  render();
  window.scrollTo({top: 0, behavior: 'smooth'});
}

function filterCat(cat) {
  currentCat = cat; currentPage = 1;
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.toggle('active', t.textContent === cat));
  if (document.getElementById('homeView').classList.contains('active')) render();
  else { showView('homeView'); render(); }
}

function doSearch() {
  searchQuery = document.getElementById('searchInput').value.trim();
  currentPage = 1; render();
}

/* ARTICLE PAGE */
function openArticlePage(id) {
  const a = articles.find(x => x.id === id); if (!a) return;
  currentArticleId = id;
  recordVisit(a);
  document.getElementById('apHero').src = a.img;
  document.getElementById('apHero').alt = a.title;
  document.getElementById('apMeta').innerHTML = `<span class="tag ${a.cat.toLowerCase()}">${a.cat}</span><span class="a-date">${a.date}</span>`;
  document.getElementById('apTitle').textContent = a.title;
  document.getElementById('apContent').innerHTML = a.content;
  const isSaved = savedIds.includes(id);
  const saveBtn = document.getElementById('artSaveBtn');
  saveBtn.classList.toggle('saved', isSaved);
  saveBtn.innerHTML = isSaved
    ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg> Saved \u2713'
    : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg> Save Article';
  const similar = articles.filter(x => x.id !== id && x.cat === a.cat).slice(0, 4);
  const fill = articles.filter(x => x.id !== id && !similar.includes(x)).reverse().slice(0, 4 - similar.length);
  document.getElementById('similarGrid').innerHTML = [...similar, ...fill].map(s => `
    <div class="similar-card" onclick="openArticlePage(${s.id})">
      <img src="${s.img}" alt="${s.title}" onerror="this.src='https://placehold.co/80x56?text=img'">
      <div class="similar-card-body">
        <div class="a-title">${s.title}</div>
        <span class="tag ${s.cat.toLowerCase()}" style="font-size:.62rem;padding:2px 6px">${s.cat}</span>
        <div class="a-date" style="margin-top:4px">${s.date}</div>
      </div>
    </div>`).join('');
  document.getElementById('nlTitle2').textContent = siteConfig.nlTitle;
  renderFooter2();
  showView('articlePageView');
}

function artToggleSave() {
  if (!currentArticleId) return;
  const saved = toggleSave(currentArticleId);
  const btn = document.getElementById('artSaveBtn');
  btn.classList.toggle('saved', saved);
  btn.innerHTML = saved
    ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg> Saved \u2713'
    : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg> Save Article';
  showToast(saved ? 'Saved \u2713' : 'Removed from saved');
}

/* FOOTER */
function buildFooterHTML() {
  const comp = footerLinks.company.map(l => `<a href="${l.url}" target="_blank" rel="noopener">${l.label}</a>`).join('');
  const res = footerLinks.resources.map(l => `<a href="${l.url}" target="_blank" rel="noopener">${l.label}</a>`).join('');
  const cats = ['Tech','Trade','Web3','Currency'].map(c => `<a href="#" onclick="filterCat('${c.toUpperCase()}');return false">${c}</a>`).join('');
  const soc = footerLinks.social.map(l => `<a href="${l.url}" target="_blank" rel="noopener" class="social-link">${l.label}</a>`).join('');
  return `<div class="footer-col"><h4>COMPANY</h4>${comp}</div><div class="footer-col"><h4>RESOURCES</h4>${res}</div><div class="footer-col"><h4>CATEGORIES</h4>${cats}</div><div class="footer-col"><h4>FOLLOW</h4>${soc}</div>`;
}
function renderFooter() {
  const g = document.getElementById('footerGrid'); if(g) g.innerHTML = buildFooterHTML();
  const d = document.getElementById('footerDesc'); if(d) d.innerHTML = siteConfig.tagline.replace(/\n/g,'<br>');
  const b = document.getElementById('footerBottom'); if(b) b.textContent = siteConfig.copyright;
}
function renderFooter2() {
  const g = document.getElementById('footerGrid2'); if(g) g.innerHTML = buildFooterHTML();
  const d = document.getElementById('footerDesc2'); if(d) d.innerHTML = siteConfig.tagline.replace(/\n/g,'<br>');
  const b = document.getElementById('footerBottom2'); if(b) b.textContent = siteConfig.copyright;
}

/* ADMIN AUTH */
function openAdminGate() {
  if (isAdmin) { openAdminPanel('customize'); return; }
  document.getElementById('pwInput').value = '';
  document.getElementById('gateErr').textContent = '';
  openOverlay('gateOverlay');
  setTimeout(() => document.getElementById('pwInput').focus(), 100);
}
async function checkPw() {
  const v = document.getElementById('pwInput').value;
  try {
    const data = await apiSend('POST', '/api/login', { password: v });
    sessionStorage.setItem('cw_admin_token', data.token);
    isAdmin = true;
    closeOverlay('gateOverlay');
    document.getElementById('adminBadge').classList.add('visible');
    document.getElementById('adminNavBtn').classList.add('active-admin');
    document.getElementById('adminBtnLabel').textContent = 'Admin \u2713';
    showToast('Admin access granted \u2713');
  } catch (e) {
    document.getElementById('gateErr').textContent = e.message;
    document.getElementById('pwInput').value = '';
    document.getElementById('pwInput').focus();
  }
}
function logoutAdmin() {
  isAdmin = false;
  sessionStorage.removeItem('cw_admin_token');
  document.getElementById('adminBadge').classList.remove('visible');
  document.getElementById('adminNavBtn').classList.remove('active-admin');
  document.getElementById('adminBtnLabel').textContent = 'Admin';
  showToast('Admin logged out');
}
async function changePassword() {
  const cur = document.getElementById('curPw').value;
  const nw = document.getElementById('newPw').value;
  const conf = document.getElementById('confirmPw').value;
  const msg = document.getElementById('pwChangeMsg');
  if (nw.length < 4) { msg.style.color='var(--red)'; msg.textContent='Min 4 characters.'; return; }
  if (nw !== conf) { msg.style.color='var(--red)'; msg.textContent='Passwords do not match.'; return; }
  try {
    await apiSend('POST', '/api/change-password', { currentPassword: cur, newPassword: nw });
    ['curPw','newPw','confirmPw'].forEach(id => document.getElementById(id).value = '');
    msg.style.color = 'var(--green)'; msg.textContent = 'Password updated!';
  } catch (e) {
    msg.style.color='var(--red)'; msg.textContent = e.message;
  }
}

/* ADMIN PANEL */
function openAdminPanel(tab) {
  if (!isAdmin) { openAdminGate(); return; }
  populateAdminPanel(); openOverlay('adminOverlay'); switchAdmTab(tab || 'customize');
}
function switchAdmTab(tab) {
  const tabs = ['customize','articles','footer','settings'];
  document.querySelectorAll('.adm-tab').forEach((t,i) => t.classList.toggle('active', tabs[i] === tab));
  document.querySelectorAll('.adm-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('adm-' + tab).classList.add('active');
}
function populateAdminPanel() {
  document.getElementById('custSiteName').value = siteConfig.name;
  document.getElementById('custTagline').value = siteConfig.tagline;
  document.getElementById('custCopyright').value = siteConfig.copyright;
  document.getElementById('custNlTitle').value = siteConfig.nlTitle;
  document.getElementById('custNlSub').value = siteConfig.nlSub;
  document.getElementById('articleMgmtList').innerHTML = [...articles].reverse().map(a => `
    <div class="article-mgmt-row">
      <img src="${a.img}" alt="${a.title}" onerror="this.src='https://placehold.co/56x40?text=img'">
      <div class="article-mgmt-info">
        <div class="a-title">${a.title}</div>
        <div class="a-date"><span class="tag ${a.cat.toLowerCase()}" style="font-size:.6rem;padding:2px 5px">${a.cat}</span> ${a.date}</div>
        <div class="adm-row">
          <button class="btn-sm gray" onclick="editArticle(${a.id})">Edit</button>
          <button class="btn-sm red" onclick="deleteArticle(${a.id})">Delete</button>
        </div>
      </div>
    </div>`).join('');
  renderFooterLinkEditor('company','footerCompanyLinks');
  renderFooterLinkEditor('resources','footerResourceLinks');
  renderFooterLinkEditor('social','footerSocialLinks');
}
async function applyCustomize() {
  siteConfig.name = document.getElementById('custSiteName').value;
  siteConfig.tagline = document.getElementById('custTagline').value;
  siteConfig.copyright = document.getElementById('custCopyright').value;
  siteConfig.nlTitle = document.getElementById('custNlTitle').value;
  siteConfig.nlSub = document.getElementById('custNlSub').value;
  try { await apiSend('PUT', '/api/config', siteConfig); render(); showToast('Changes saved!'); }
  catch (e) { showToast('Save failed: ' + e.message); }
}
async function resetCustomize() {
  siteConfig = {name:'CommerceWorld',tagline:'The premium digital commerce news platform.\nNavigating trade, technology, and Web3.',copyright:'\u00a9 2026 CommerceWorld. All rights reserved. Built for the future of digital commerce.',nlTitle:'STAY AHEAD OF THE CURVE',nlSub:'Get the latest commerce intelligence delivered to your inbox.'};
  try { await apiSend('PUT', '/api/config', siteConfig); populateAdminPanel(); render(); showToast('Reset to defaults'); }
  catch (e) { showToast('Save failed: ' + e.message); }
}
function applyColor(v,val){document.documentElement.style.setProperty(v,val)}
function applyFont(font){document.body.style.fontFamily=font+',sans-serif';document.getElementById('fontPreview').style.fontFamily=font+',sans-serif'}
async function deleteArticle(id){
  if(!confirm('Delete this article?'))return;
  try { await apiSend('DELETE', '/api/articles/' + id); articles=articles.filter(a=>a.id!==id); populateAdminPanel(); render(); showToast('Article deleted'); }
  catch (e) { showToast('Delete failed: ' + e.message); }
}
function editArticle(id){const a=articles.find(x=>x.id===id);if(!a)return;editingId=id;document.getElementById('editorModalTitle').textContent='Edit Article';document.getElementById('articleTitleInput').value=a.title;document.getElementById('editorArea').innerHTML=a.content;document.getElementById('catSelect').value=a.cat;document.getElementById('excerptInput').value=a.excerpt;document.getElementById('coverInput').value=a.img;closeOverlay('adminOverlay');openOverlay('editorOverlay')}
async function clearAllArticles(){
  if(!confirm('Delete ALL articles? This cannot be undone.'))return;
  try { await Promise.all(articles.map(a => apiSend('DELETE', '/api/articles/' + a.id))); articles=[]; populateAdminPanel(); render(); showToast('All articles deleted'); }
  catch (e) { showToast('Delete failed: ' + e.message); }
}
function renderFooterLinkEditor(section,containerId){document.getElementById(containerId).innerHTML=footerLinks[section].map((l,i)=>`<div class="footer-link-row"><input type="text" value="${l.label}" oninput="footerLinks['${section}'][${i}].label=this.value" placeholder="Label"><input type="url" value="${l.url}" oninput="footerLinks['${section}'][${i}].url=this.value" placeholder="URL"><button onclick="removeFooterLink('${section}',${i})">&#x2715;</button></div>`).join('')}
function removeFooterLink(section,i){footerLinks[section].splice(i,1);renderFooterLinkEditor(section,`footer${section.charAt(0).toUpperCase()+section.slice(1)}Links`)}
function addFooterLink(section){const lId='new'+section.charAt(0).toUpperCase()+section.slice(1)+'Label';const uId='new'+section.charAt(0).toUpperCase()+section.slice(1)+'Url';const label=document.getElementById(lId).value.trim();const url=document.getElementById(uId).value.trim()||'#';if(!label){showToast('Enter a label');return;}footerLinks[section].push({label,url});document.getElementById(lId).value='';document.getElementById(uId).value='';renderFooterLinkEditor(section,`footer${section.charAt(0).toUpperCase()+section.slice(1)}Links`)}
async function saveFooterLinks(){
  try { await apiSend('PUT', '/api/footer-links', footerLinks); renderFooter(); renderFooter2(); closeOverlay('adminOverlay'); showToast('Footer links saved!'); }
  catch (e) { showToast('Save failed: ' + e.message); }
}

/* EDITOR */
function openEditor(){if(!isAdmin){openAdminGate();return;}editingId=null;document.getElementById('editorModalTitle').textContent='New Article';document.getElementById('articleTitleInput').value='';document.getElementById('editorArea').innerHTML='';document.getElementById('excerptInput').value='';document.getElementById('coverInput').value='';openOverlay('editorOverlay');setTimeout(()=>document.getElementById('articleTitleInput').focus(),100)}
let savedRange=null;
document.addEventListener('selectionchange',()=>{const ea=document.getElementById('editorArea');const sel=window.getSelection();if(ea&&sel&&sel.rangeCount>0&&ea.contains(sel.anchorNode))savedRange=sel.getRangeAt(0).cloneRange()});
function restoreRange(){if(!savedRange)return;const sel=window.getSelection();sel.removeAllRanges();sel.addRange(savedRange)}
function execCmd(cmd,val){restoreRange();document.execCommand(cmd,false,val||null);document.getElementById('editorArea').focus()}
function insertLink(){const url=prompt('Enter URL:','https://');if(url)execCmd('createLink',url)}
function toggleInsertPanel(){document.getElementById('insertPanel').classList.toggle('open')}
function insertImageFile(){const file=document.getElementById('imgFile').files[0];if(!file)return;const reader=new FileReader();reader.onload=e=>{restoreRange();document.execCommand('insertImage',false,e.target.result);toggleInsertPanel();document.getElementById('imgFile').value=''};reader.readAsDataURL(file)}
function insertImageUrl(){const url=document.getElementById('imgUrl').value.trim();if(!url)return;restoreRange();document.execCommand('insertImage',false,url);document.getElementById('imgUrl').value='';toggleInsertPanel()}
function saveDraft(){showToast('Draft saved!')}
async function publishArticle(){
  const title=document.getElementById('articleTitleInput').value.trim();
  const content=document.getElementById('editorArea').innerHTML.trim();
  const cat=document.getElementById('catSelect').value;
  const excerpt=document.getElementById('excerptInput').value.trim();
  const cover=document.getElementById('coverInput').value.trim();
  if(!title||!content){showToast('Add a title and content first');return;}
  const now=new Date();
  const date=`${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}/${now.getFullYear()}`;
  const randImg=IMGS[Math.floor(Math.random()*IMGS.length)];
  const finalExcerpt = excerpt||title.substring(0,90)+'...';
  try {
    if(editingId){
      const idx=articles.findIndex(a=>a.id===editingId);
      const img = cover||(idx>=0?articles[idx].img:randImg);
      await apiSend('PUT', '/api/articles/' + editingId, {title,content,cat,excerpt:finalExcerpt,img});
      if(idx>=0) articles[idx]={...articles[idx],title,content,cat,excerpt:finalExcerpt,img};
      editingId=null; showToast('Article updated!');
    } else {
      const img = cover||randImg;
      const {id} = await apiSend('POST', '/api/articles', {title,content,cat,date,excerpt:finalExcerpt,img});
      articles.push({id,title,content,cat,date,excerpt:finalExcerpt,img});
      showToast('Published! \uD83C\uDF89');
    }
  } catch (e) { showToast('Publish failed: ' + e.message); return; }
  closeOverlay('editorOverlay');currentCat='LATEST';currentPage=1;
  document.querySelectorAll('.cat-tab').forEach(t=>t.classList.toggle('active',t.textContent==='LATEST'));
  render();
}

/* OVERLAY HELPERS */
function openOverlay(id){document.getElementById(id).classList.add('open')}
function closeOverlay(id){document.getElementById(id).classList.remove('open')}
['editorOverlay','adminOverlay','gateOverlay'].forEach(id=>{document.getElementById(id).addEventListener('click',e=>{if(e.target===document.getElementById(id))closeOverlay(id)})});

/* THEME */
function toggleTheme(){const html=document.documentElement;const isLight=html.getAttribute('data-theme')==='light';html.setAttribute('data-theme',isLight?'dark':'light');document.getElementById('moonIcon').style.display=isLight?'block':'none';document.getElementById('sunIcon').style.display=isLight?'none':'block'}

/* DRAWER */
function openDrawer(){updateLibraryUI();document.getElementById('drawer').classList.add('open');document.getElementById('scrim').classList.add('open')}
function closeDrawer(){document.getElementById('drawer').classList.remove('open');document.getElementById('scrim').classList.remove('open')}

/* TOAST + NEWSLETTER */
function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2400)}
function subscribe(){const v=document.getElementById('emailInput').value.trim();if(!v||!v.includes('@')){showToast('Enter a valid email');return;}document.getElementById('emailInput').value='';showToast('Subscribed! Welcome \uD83C\uDF89')}
function subscribe2(){const v=document.getElementById('emailInput2').value.trim();if(!v||!v.includes('@')){showToast('Enter a valid email');return;}document.getElementById('emailInput2').value='';showToast('Subscribed! Welcome \uD83C\uDF89')}

/* INIT */
loadFromServer();
updateLibraryUI();
if (adminToken()) {
  isAdmin = true;
  document.getElementById('adminBadge').classList.add('visible');
  document.getElementById('adminNavBtn').classList.add('active-admin');
  document.getElementById('adminBtnLabel').textContent = 'Admin \u2713';
}
</script>
</body>
</html>"""


# ── Frontend route ────────────────────────────────────────────

@app.route('/')
def index():
    return HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

# ── Auth ──────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    body = request.get_json(force=True) or {}
    password = body.get('password', '')
    auth = load_auth()
    if hash_pw(password) == auth['password_hash']:
        token = secrets.token_hex(32)
        valid_tokens.add(token)
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/change-password', methods=['POST'])
def change_password():
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    body = request.get_json(force=True) or {}
    cur = body.get('currentPassword', '')
    new = body.get('newPassword', '')
    auth = load_auth()
    if hash_pw(cur) != auth['password_hash']:
        return jsonify({'error': 'Current password is incorrect'}), 400
    if len(new) < 4:
        return jsonify({'error': 'New password must be at least 4 characters'}), 400
    auth['password_hash'] = hash_pw(new)
    save_auth(auth)
    valid_tokens.clear()
    return jsonify({'ok': True})

# ── Config ────────────────────────────────────────────────────

@app.route('/api/config', methods=['GET'])
def get_config():
    data = load_data()
    return jsonify(data.get('config', {}))

@app.route('/api/config', methods=['PUT'])
def put_config():
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    data = load_data()
    body = request.get_json(force=True) or {}
    data['config'] = body
    save_data(data)
    return jsonify({'ok': True})

# ── Articles ──────────────────────────────────────────────────

@app.route('/api/articles', methods=['GET'])
def get_articles():
    data = load_data()
    return jsonify(data.get('articles', []))

@app.route('/api/articles', methods=['POST'])
def create_article():
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    data = load_data()
    articles = data.get('articles', [])
    body = request.get_json(force=True) or {}
    new_id = max((a['id'] for a in articles), default=0) + 1
    body['id'] = new_id
    articles.append(body)
    data['articles'] = articles
    save_data(data)
    return jsonify({'id': new_id}), 201

@app.route('/api/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    data = load_data()
    articles = data.get('articles', [])
    idx = next((i for i, a in enumerate(articles) if a['id'] == article_id), None)
    if idx is None:
        return jsonify({'error': 'Not found'}), 404
    body = request.get_json(force=True) or {}
    body['id'] = article_id
    articles[idx] = body
    data['articles'] = articles
    save_data(data)
    return jsonify({'ok': True})

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    data = load_data()
    data['articles'] = [a for a in data.get('articles', []) if a['id'] != article_id]
    save_data(data)
    return jsonify({'ok': True})

# ── Footer Links ──────────────────────────────────────────────

@app.route('/api/footer-links', methods=['GET'])
def get_footer_links():
    data = load_data()
    return jsonify(data.get('footerLinks', {'company': [], 'resources': [], 'social': []}))

@app.route('/api/footer-links', methods=['PUT'])
def put_footer_links():
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    data = load_data()
    body = request.get_json(force=True) or {}
    data['footerLinks'] = body
    save_data(data)
    return jsonify({'ok': True})

# ── Run ───────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
