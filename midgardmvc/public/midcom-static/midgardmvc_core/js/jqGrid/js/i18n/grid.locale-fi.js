;(function($){
/**
 * jqGrid (fi) Finnish Translation
 * Jukka Inkeri  awot.fi
 * http://awot.fi
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
**/
$.jgrid = {
	defaults : {
		recordtext: "Tulokset {0} - {1} / {2}",
	    emptyrecords: "Ei tuloksia",
		loadtext: "Haetaan...",
		pgtext : "Sivu {0} / {1}"
	},
	search : {
	    caption: "Etsi...",
	    Find: "Etsi",
	    Reset: "Tyhj&auml;&auml;",
	    odata : ['equal', 'not equal', 'less', 'less or equal','greater','greater or equal', 'begins with','does not begin with','is in','is not in','ends with','does not end with','contains','does not contain'],
	    groupOps: [	{ op: "AND", text: "all" },	{ op: "OR",  text: "any" }	],
		matchText: " match",
		rulesText: " rules"
	},
	edit : {
	    addCaption: "Uusi rivi",
	    editCaption: "Muokkaa rivi",
	    bSubmit: "OK",
	    bCancel: "Peruuta",
		bClose: "Sulje",
		saveData: "Tiedot ovat muuttuneet! Tallennetaanko?",
		bYes : "Kyllä",
		bNo : "Ei",
		bExit : "Peruuta",
	    msg: {
	        required: "pakollinen",
	        number:"Anna kelvollinen nro",
	        minValue:"arvo oltava >= ",
	        maxValue:"arvo oltava  <= ",
	        email: "virheellinen sposti ",
	        integer: "Anna kelvollinen kokonaisluku",
			date: "Anna kelvollinen pvm",
			url: "virheellinen URL. Lis&auml;&auml; ('http://' tai 'https://')"
		}
	},
	view : {
	    caption: "Tarkastele riviä",
	    bClose: "Sulje"
	},
	del : {
	    caption: "Poista",
	    msg: "Poista valitut rivi(t)?",
	    bSubmit: "Poista",
	    bCancel: "Peruuta"
	},
	nav : {
		edittext: " ",
	    edittitle: "Muokkaa valittua rivi",
		addtext:" ",
	    addtitle: "Uusi rivi",
	    deltext: " ",
	    deltitle: "Poista valittu rivi",
	    searchtext: " ",
	    searchtitle: "Etsi tietoja",
	    refreshtext: "",
	    refreshtitle: "Päivitä",
	    alertcap: "Varoitus",
	    alerttext: "Valitse rivi",
		viewtext: "",
		viewtitle: "Tarkastele valittua rivi&auml;"
	},
	col : {
	    caption: "Nayt&auml; / Piilota sarakkeet",
	    bSubmit: "OK",
	    bCancel: "Peruuta"	
	},
	errors : {
		errcap : "Virhe",
		nourl : "URL asettamatta",
		norecords: "Ei muokattavia tietoja",
	    model : "M&auml;&auml;ritetyt colNames -arvot ei t&auml;sm&auml; colModel -arvoihin!"
	},
	formatter : {
		integer : {thousandsSeparator: "", defaultValue: '0'},
		number : {decimalSeparator:",", thousandsSeparator: "", decimalPlaces: 2, defaultValue: '0,00'},
		currency : {decimalSeparator:",", thousandsSeparator: "", decimalPlaces: 2, prefix: "", suffix:"", defaultValue: '0,00'},
		date : {
			dayNames:   [
				"Su", "Ma", "Ti", "Ke", "To", "Pe", "La",
				"Sunnuntai", "Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai", "Lauantai"
			],
			monthNames: [
				"Tam", "Hel", "Maa", "Huh", "Tou", "Kes", "Hei", "Elo", "Syy", "Lok", "Mar", "Jou",
				"Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu", "Toukokuu", "Kes&auml;kuu", "Hein&auml;kuu", "Elokuu", "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
			],
			AmPm : ["am","pm","AM","PM"],
			S: function (j) {return j < 11 || j > 13 ? ['st', 'nd', 'rd', 'th'][Math.min((j - 1) % 10, 3)] : 'th'},
			srcformat: 'Y-m-d',
			newformat: 'd.m.Y',
			masks : {
	            ISO8601Long:"Y-m-d H:i:s",
	            ISO8601Short:"Y-m-d",
	            ShortDate: "d.m.Y",
	            LongDate: "l, F d, Y",
	            FullDateTime: "l, F d, Y g:i:s A",
	            MonthDay: "F d",
	            ShortTime: "g:i A",
	            LongTime: "g:i:s A",
	            SortableDateTime: "Y-m-d\\TH:i:s",
	            UniversalSortableDateTime: "Y-m-d H:i:sO",
	            YearMonth: "F, Y"
	        },
	        reformatAfterEdit : false
		},
		baseLinkUrl: '',
		showAction: '',
	    target: '',
	    checkbox : {disabled:true},
		idName : 'id'
	}
};
// FI
})(jQuery);
