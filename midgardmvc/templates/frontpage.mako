<%inherit file="/base/default.mako" />

<%def name="body()">

% if c.page.guid:
	<h1>${c.page.title}</h1>
	
	${h.literal(c.page.content)}
% endif

</%def>