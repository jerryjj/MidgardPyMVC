function jqGridInclude(options)
{
    var options = jQuery.extend({
        locale: 'en',
        jspath: 'jqGrid/js/',
        modules: []
    }, options || {});

    var modules = [
        { incfile: 'i18n/grid.locale-'+options.locale+'.js' },
        { incfile: 'grid.base.js' },
        { incfile: 'grid.custom.js' },
        { incfile: 'jquery.fmatter.js' }
    ];
    
    jQuery.each(options.modules, function(i, module) {
        modules.push({
            incfile: module
        });
    });
    
    var filename;
    
    for (var i=0;i<modules.length; i++) {
    	filename = options.jspath + modules[i].incfile;
    	
   		if (jQuery.browser.safari) {
   			jQuery.ajax({url: filename, dataType: 'script', async: false, cache: true});
   		} else {
   			includeJavaScript(filename);
   		}
    }
    
    function includeJavaScript(jsFile)
    {
        var oHead = document.getElementsByTagName('head')[0];
        var oScript = document.createElement('script');
        
        oScript.type = 'text/javascript';
        oScript.charset = 'utf-8';
        oScript.src = jsFile;
        
        oHead.appendChild(oScript);        
    };
};
jqGridInclude(jqGridIncludeConfig);
var grid_image_path = 'themes/basic/images';