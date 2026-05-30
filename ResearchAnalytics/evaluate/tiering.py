"""Deterministic source-tier normalization.

Tiers are otherwise assigned ad-hoc by the model in each stage, which drifts
(the same URL can come back T1 in one call and T2 in another). This module is the
single code-side authority: for any URL whose domain matches a known rule, the tier
is corrected to the rule's value; unknown domains keep the model's chosen tier.

Rigor lives in code, not prompt discipline — same philosophy as the claim contract.
"""
from urllib.parse import urlparse
from .contracts import SourceTier, Evidence, Claim, Case, Positions

# Domain substring -> tier. Order does not matter; first match wins on iteration,
# so keep entries mutually exclusive. Matching is on the registered/host suffix.
_DOMAIN_TIERS: dict[str, SourceTier] = {
    # T1 — primary data / official statistics / government records
    "congress.gov": SourceTier.T1,
    "loc.gov": SourceTier.T1,
    ".gov": SourceTier.T1,
    ".gov.uk": SourceTier.T1,
    "oecd.org": SourceTier.T1,
    "europa.eu": SourceTier.T1,
    "kela.fi": SourceTier.T1,
    # T2 — peer-reviewed / academic
    ".edu": SourceTier.T2,
    "ac.uk": SourceTier.T2,
    "nber.org": SourceTier.T2,
    "ssrn.com": SourceTier.T2,
    "doi.org": SourceTier.T2,
    "ncbi.nlm.nih.gov": SourceTier.T2,
    # T3 — reputable secondary (established journalism / reference)
    "wikipedia.org": SourceTier.T3,
    "investopedia.com": SourceTier.T3,
    "britannica.com": SourceTier.T3,
    "reuters.com": SourceTier.T3,
    "apnews.com": SourceTier.T3,
    "bbc.com": SourceTier.T3,
    "bbc.co.uk": SourceTier.T3,
    "theguardian.com": SourceTier.T3,
    "nytimes.com": SourceTier.T3,
    "economist.com": SourceTier.T3,
    "mckinsey.com": SourceTier.T3,
    # T4 — advocacy / opinion / think tanks / social
    "cato.org": SourceTier.T4,
    "aei.org": SourceTier.T4,
    "rooseveltinstitute.org": SourceTier.T4,
    "epi.org": SourceTier.T4,
    "facebook.com": SourceTier.T4,
    "twitter.com": SourceTier.T4,
    "x.com": SourceTier.T4,
    "medium.com": SourceTier.T4,
}


def tier_for(url: str, fallback: SourceTier) -> SourceTier:
    """Authoritative tier for a URL; falls back to the model's tier if domain unknown."""
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return fallback
    if not host:
        return fallback
    for domain, tier in _DOMAIN_TIERS.items():
        if host == domain.lstrip(".") or host.endswith(domain):
            return tier
    return fallback


def normalize_evidence(items: list[Evidence]) -> list[Evidence]:
    for e in items:
        e.tier = tier_for(e.url, e.tier)
    return items


def normalize_claim(c: Claim) -> Claim:
    normalize_evidence(c.data)
    return c


def normalize_positions(p: Positions) -> Positions:
    for group in (p.pro, p.against, p.inbetween):
        for c in group:
            normalize_claim(c)
    return p


def normalize_case(c: Case) -> Case:
    """Cases carry one tier for the whole row; correct it to the strongest (lowest-number)
    tier among its sources whose domain we recognize, else leave the model's tier."""
    known = [tier_for(u, None) for u in c.source_urls]
    known = [t for t in known if t is not None]
    if known:
        c.tier = min(known)
    return c
