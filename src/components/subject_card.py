import html

import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    safe_name = html.escape(str(name))
    safe_code = html.escape(str(code))
    safe_section = html.escape(str(section))

    parts = [
        '<div style="background:#fffaf1;border-left:5px solid #a7624b;'
        'padding:22px;border-radius:8px;border:1px solid #d8c7ac;'
        'margin-bottom:18px;box-shadow:0 10px 28px rgba(54,48,39,0.06);">',
        f'<h3 style="margin:0;color:#2f2a24;font-size:1.22rem;">{safe_name}</h3>',
        '<p style="color:#6f6659;margin:10px 0 14px;">'
        'Code: '
        '<span style="background:#efe3cf;color:#405449;padding:3px 9px;'
        'border-radius:5px;font-weight:700;border:1px solid #d8c7ac;">'
        f'{safe_code}</span>&nbsp; Section: {safe_section}</p>',
    ]

    if stats:
        parts.append('<div style="display:flex;gap:8px;flex-wrap:wrap;">')
        for icon, label, value in stats:
            safe_icon = html.escape(str(icon))
            safe_label = html.escape(str(label))
            safe_value = html.escape(str(value))
            parts.append(
                '<div style="background:#f1e8d8;color:#3a352e;padding:6px 12px;'
                'border-radius:6px;border:1px solid #d8c7ac;font-size:0.9rem;">'
                f'{safe_icon} <b>{safe_value}</b> {safe_label}</div>'
            )
        parts.append('</div>')

    parts.append('</div>')

    st.markdown("".join(parts), unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
