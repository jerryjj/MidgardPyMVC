<%inherit file="/base/default.mako" />

<%def name="body()">

% if c.page.guid:
	<h1>${c.page.title}</h1>
	
	${h.literal(c.page.content)}
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