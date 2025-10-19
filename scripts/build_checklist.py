# (same header + imports as your latest version)
# ... keep existing code unchanged up to the final markdown assembly ...

    md.append("\n## 🔎 Deep Searches Pending – Events\n")
    md.append(render_table(["Date","Location","Event","Participants (on record)","Search Notes"], sections["deep_event"]))

    md.append("\n## 🔎 Deep Searches Pending – People at Events\n")
    md.append(render_table(["Date","Location","Event","Person","Role","Search Notes"], sections["deep_people"]))

    # NEW: Unverified sections
    # Load unverified CSVs
    ue = read_csv(DATA / "unverified_events.csv", ["date","location","event","primary_source","secondary_source","confidence","notes","next_step"])
    up = read_csv(DATA / "unverified_people.csv", ["person","possible_event_date","location","alleged_association","source","confidence","notes","next_step"])
    uc = read_csv(DATA / "unverified_connections.csv", ["entity_a","entity_b","connection_type","source","confidence","notes","next_step"])

    # Only show items that are not clearly 'verified'
    ue = [r for r in ue if r.get("confidence","").lower() != "verified"]
    up = [r for r in up if r.get("confidence","").lower() != "verified"]
    uc = [r for r in uc if r.get("confidence","").lower() != "verified"]

    md.append("\n## 🔸 Unverified Events – Awaiting Verification\n")
    md.append(render_table(["Date","Location","Event","Primary Source","Secondary Source","Confidence","Next Step"], [[r["date"], r["location"], r["event"], r["primary_source"], r["secondary_source"], r["confidence"], r["next_step"]] for r in ue]))

    md.append("\n## 🔸 Unverified People – Awaiting Cross-Confirmation\n")
    md.append(render_table(["Person","Possible Date","Location","Alleged Association","Source","Confidence","Next Step"], [[r["person"], r["possible_event_date"], r["location"], r["alleged_association"], r["source"], r["confidence"], r["next_step"]] for r in up]))

    md.append("\n## 🔸 Unverified Connections – Leads Needing Validation\n")
    md.append(render_table(["Entity A","Entity B","Connection Type","Source","Confidence","Next Step"], [[r["entity_a"], r["entity_b"], r["connection_type"], r["source"], r["confidence"], r["next_step"]] for r in uc]))

    (ROOT / "CHECKLIST.md").write_text("\n".join(md), encoding="utf-8")
    print("Updated CHECKLIST.md")
