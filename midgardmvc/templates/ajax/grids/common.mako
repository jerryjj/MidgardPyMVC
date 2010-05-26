<?xml version="1.0" encoding="utf-8"?>
<rows>
    <page>${c.pages['page']}</page>
    <total>${c.pages['total']}</total>
    <records>${c.pages['total_rows']}</records>
    
	% if c.userdata:
		% for key, value in c.userdata.items():		
        <userdata name="${key}" tal:content="${value}" />
		% endfor
	% endif
    
	% for row in c.rows:
    <row id="${row[c.row_id_column]}">
		% for cell in c.cells:
        <cell>${row[cell]}</cell>
		% endfor
    </row>
	% endfor
</rows>