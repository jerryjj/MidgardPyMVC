<%inherit file="/base/default.mako" />

<%def name="body()">

<h1>${c.node.title}</h1>

${h.literal(c.node.content)}

</%def>