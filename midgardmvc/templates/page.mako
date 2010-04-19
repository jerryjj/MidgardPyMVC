<%inherit file="/base/default.mako" />

<%def name="body()">

<h1>${c.page.title}</h1>

${h.literal(c.page.content)}

</%def>