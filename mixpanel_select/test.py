from mixpanel_select import MixpanelSelect

from datetime import datetime

if __name__ == '__main__':
    # This map will drive everything
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
			'event_name' : 'Offer Page Load',
			'type' : 'unique',
			'where' : {
			    '$city' : ['Seattle', 'Washington'],
			    '$os' : ['Windows']
			    }
		    },
		    {
			'event_name' : 'Promotion Popup Load',
			'type' : 'unique',
			'where' : {
			    '$os' : ['Windows', 'Mac OS X']
			    }
		    }
		    ],
		'Likes' : [
		    {
			'event_name' : 'Like Click',
			'type' : 'unique',
			'where' : {
			    'mp_country_code' : ['US', 'GB'],
			    }
		    }
		    ]
		},
	    'on' : 'merchant_key'
	}
    m = MixpanelSelect(mixpanel_api_key = '<your-mixpanel-api-key>', 
	    mixpanel_api_secret = '<your-mixpanel-api-secret>', global_map = global_map)
    print m.get_data()
