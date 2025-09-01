
from urllib.parse import urlsplit
import re

BRANDS = {"paypal","apple","bank","chase","amazon","microsoft","facebook","instagram","whatsapp","google","netflix"}
SUSP_TLDS = {"ru","cn","tk","ml","ga","gq","cf","xyz","top","club","click","work","rest","zip","mov"}
IPV4_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

def _hostname(netloc: str) -> str:
    if "@" in netloc: netloc = netloc.split("@",1)[1]
    if ":" in netloc: netloc = netloc.split(":",1)[0]
    return netloc.lower()

def extract_features(url: str) -> dict:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = _hostname(parts.netloc or "")
    path = parts.path or ""
    query = parts.query or ""
    host_labels = [h for h in host.split(".") if h]
    tld = host_labels[-1] if host_labels else ""
    subdomains = host_labels[:-2] if len(host_labels)>=2 else []
    domain = host_labels[-2] if len(host_labels)>=2 else (host_labels[0] if host_labels else "")
    has_ip = bool(IPV4_RE.match(host))
    has_at = "@" in parts.netloc
    is_puny = host.startswith("xn--")
    digits_in_host = sum(c.isdigit() for c in host)
    hyphens_in_host = host.count("-")
    dots = url.count(".")
    specials = sum(url.count(ch) for ch in ["?","&","%","=","_"])
    brand_hits = sum(1 for b in BRANDS if b in url.lower())
    brand_mismatch = 1 if (brand_hits>0 and domain not in BRANDS) else 0
    susp_tokens = sum((path+"?"+query).lower().count(tok) for tok in ["login","verify","update","secure","account","confirm"])
    feats = {
        "url_len": len(url),
        "host_len": len(host),
        "path_len": len(path),
        "query_len": len(query),
        "dots": dots,
        "specials": specials,
        "subdomain_count": len(subdomains),
        "has_ip": int(has_ip),
        "has_at": int(has_at),
        "is_puny": int(is_puny),
        "http_scheme": int(scheme=="http"),
        "digits_in_host": digits_in_host,
        "hyphens_in_host": hyphens_in_host,
        "suspect_tld": int(tld in SUSP_TLDS),
        "brand_hits": brand_hits,
        "brand_mismatch": brand_mismatch,
        "susp_tokens": float(susp_tokens),
    }
    feats["rule_score"] = min(1.0, 0.3*feats["http_scheme"] + 0.35*feats["has_ip"] + 0.1*min(3,feats["subdomain_count"]) + 0.15*feats["suspect_tld"] + 0.1*feats["brand_mismatch"])
    return feats

FEAT_ORDER = ["url_len","host_len","path_len","query_len","dots","specials","subdomain_count","has_ip","has_at","is_puny","http_scheme","digits_in_host","hyphens_in_host","suspect_tld","brand_hits","brand_mismatch","susp_tokens","rule_score"]
