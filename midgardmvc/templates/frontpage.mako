<%inherit file="/base/default.mako" />

<%def name="body()">

% if c.node.guid:
	<h1>${c.node.title}</h1>
	
	${h.literal(c.node.content)}
% endif

<br />

% if c.user:
	Username: ${c.user.login}<br />
% endif

% if c.person:
	Person GUID: ${c.person.guid}<br />
	Firstname: ${c.person.firstname}<br />
	Lastname: ${c.person.lastname}<br />
% endif

</%def>