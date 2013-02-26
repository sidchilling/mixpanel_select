from mixpanel_select import MixpanelSelect

from datetime import datetime

if __name__ == '__main__':
    global_map = {
	    'to_date' : datetime.strptime('2013-02-25', '%Y-%m-%d'),
	    'from_date' : datetime.strptime('2012-12-28', '%Y-%m-%d'),
	    'where' : {
		'merchant_key' : ['cafepress', 'canvasondemand'], 
		'$browser' : ['Internet Explorer']
		},
	    'metrics' : {
		'Page Load' : [
		    {
			'event_name' : 'Offer Page Load', # cafepress - 1467, canvasondemand - 397
			'type' : 'unique',
			'where' : {
			    '$city' : ['Seattle', 'Washington'],
			    '$os' : ['Windows']
			    }
		    },
		    {
			'event_name' : 'Promotion Popup Load', # cafepress - 192, canvasondemand - 53
			'type' : 'unique',
			'where' : {
			    '$os' : ['Windows', 'Mac OS X']
			    }
		    }
		    ],
		'Likes' : [
		    {
			'event_name' : 'Like Click', #cafepress - 7462, canvasondemand - 1987
			'type' : 'unique',
			'where' : {
			    'mp_country_code' : ['US', 'GB'],
			    }
		    }
		    ]
		},
	    'on' : 'merchant_key'
	}
    m = MixpanelSelect(mixpanel_api_key = 'your-mixpanel-api-key', 
	    mixpanel_api_secret = 'your-mixpanel-api-secret', global_map = global_map)
    print m.get_data()
