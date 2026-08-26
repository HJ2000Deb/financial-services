# Connectors and governance

What Claude is connected to, who connects it, and where the boundaries sit.

## The rule that matters

**Nobody connects Claude to anything themselves.** Connectors are configured centrally, by
Holly, with the tenancy admin. An individual who authorises a connector is making a data
decision on behalf of the firm and its clients, and that is not theirs to make.

## What is connected, and what each is for

| Connector | Reads | Writes | Used by |
|---|---|---|---|
| **SharePoint / OneDrive** (Microsoft 365) | Deal folders, data packs, templates | Only into `out/` on the deal folder | Every stage |
| **Outlook** | Correspondence, for log reconciliation and history | **Drafts only, to the compose pane** | Outreach, process updates, debriefs |
| **Teams** | Deal-team chat for context on what was agreed | No | Debriefs, process updates |
| **CRM** | Pipeline, relationships, approach history | Records on approved names | Origination, pipeline review |
| **PitchBook** | Sponsors, funds, investors, deals | No | Origination, buyer universe, pitch |
| **Grata** | Private company search, financials, buyers, transactions | Lists, where approved | Origination, buyer universe |
| **Companies House** | Filed accounts, directors, shareholdings | No | Screening, dossiers, verification |

Three connectors are declared in `.mcp.json` with placeholder URLs — Grata, Microsoft 365
and the CRM — because those endpoints belong to the tenancy, not to this repository. A
connector with no URL does not load, and the skills fall back to asking for the document.

## Write access, deliberately narrow

| Action | Who can do it |
|---|---|
| Send an email | A person, from their own compose pane |
| Issue a document to a buyer or vendor | A person, after partner review |
| Write a file into a deal folder | An agent, into `out/` only, dated |
| Move a file out of `out/` into the numbered folders | A person, after review |
| Create or update a CRM record | An agent, on names a person has approved |
| Delete anything | A person. Claude requires explicit permission before permanently removing any file |

## What changed on Claude Team, and what did not

**Now permitted**

- Client and deal material may be used within the Debrett's organisation.
- The organisation runs under Anthropic's commercial terms, with content excluded from
  model training by default.
- Documents can be loaded into Projects and shared with the deal team.
- Connectors to our own systems are enabled centrally as governance allows.

**Still applies**

- Use your Debrett's account. Personal or free Claude accounts are not for firm work.
- Client confidentiality and engagement terms are unchanged by the tool you use.
- Do not connect Claude to any system yourself.
- Everything that leaves the firm carries your name and your verification.

## Before a mandate goes into a Project

1. Check the engagement terms for any restriction on AI use. If there is one, or if the
   matter is unusually sensitive, speak to Holly before loading anything.
2. Confirm the Project is shared with the deal team and nobody else.
3. Confirm no other client's material is in the Project.

## The sensible test

Treat Claude as a capable new joiner who has signed the same confidentiality undertakings
you have. You would give them the data pack; you would not give them the client's password.
You would ask them to draft the Q&A; you would still read it before it went out.

## Agent permissions

Agents run with least privilege, and it is visible in each cookbook:

- Readers hold read tools and read-only connectors. No write, no send.
- Exactly one worker per agent holds `Write`, and it writes only into `out/`.
- No agent in this repository holds an email or messaging send tool. Client contact happens
  outside the agent, by a person.
- Approval mode: **Manual** for anything touching a client system on a live mandate. Auto
  is acceptable for internal assembly on a mandate already in the Project. Skip is not used
  on client work.
