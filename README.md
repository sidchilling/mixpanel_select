MixpanelSelect
===============

This is a library which can be used to select segmented data using the Mixpanel API. In my experience, often times
I need to extract data using the Mixpanel API on different where conditions and aggregate them. This results in
boiler plate code which I have to write everytime. 

This library is an attempt to provide an easy way to segment data on various where conditions and aggregate them
using a simple configuration map. By aggregating data, I mean that I can define a metric consisting of various 
`events` and `where` conditions. 

A simple configuration map can be written as follows -

```
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

```

In the map, everything that you need has been defined. The meaning of the various fields are  -

1. `from_date` : From date for selecting the data. This will be applied to all the `events`.
2. `to_date` : Until date for selecting the data. This will be applied to all the `events`.
3. `on` : This is the `BY` clause in mixpanel. This can be thought of as a `GROUP BY` clause when thought in SQL terms.
4. `where` : The where conditions to be applied globally, that is, to all the events.
5. `metrics` : A list of metrics that you need to select. A metric is composed of one or more `events`.

Defining the `where` conditions is easy, you just have a key with the where condition name and the value is always
a list of possible values for the key. 
Example - if `where` is - 
```
{
  'merchant_key' : ['cafepress', 'cannvasondemand'],
  '$browser' : ['Internet Explorer']
}
```
then, the corresponding where expression will be -
```
("cafepress" == properties["merchant_key"] or "canvasondemand" == properties["merchant_key"]) and 
("Internet Explorer" == properties["$browser"])
```

The similar pattern is followed for the `event` level `where` conditions as well.

Now, for the `metrics` value, it is always a list of metrics you want to extract from mixpanel. A metric
is defined as a group of `events`. So if there are two `events` in a metric, then the value of the metric is
the sum of the two `events`.

Taking the example of one metric from the above global map, we need to understand what will be the where expression 
formed and what will be the value of the metric.

```
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
		    ]
```

So, the final result for `Page Load` it is as follows -

`Page Load` = (Value of `Offer Page Load` with the where expression `where1`) + (Value of `Promotion Popup Load` with where expression `where2`)

`where1` and `where2` expresions are formed keeping in mind the global `where` as well as event level `wheres`. So -
```
where1 = ("cafepress" == properties["merchant_key"] or "canvasondemand" == properties["merchant_key"]) and
("Internet Explorer" == properties["$browser"]) and ("Windows" == properties["$os"]) and 
("Seattle" == properties["$city"] or "Washington" == properties["$city"])
```

```
where2 = ("cafepress" == properties["merchant_key"] or "canvasondemand" == properties["merchant_key"]) and
("Internet Explorer" == properties["$browser"]) and ("Windows" == properties["$os"] or 
"Mac OS X" == properties["$os"])
```

The `type` key in the event maps are the type you want to select - `unique`, `general`, `total`

Now, to use the library you should make an instance of the class and call the `get_data()` function -

```
m = MixpanelSelect(mixpanel_api_key = 'your-mixpanel-api-key', mixpanel_api_secret = 'your-mixpanel-api-secret',
  global_map = global_map)
print m.get_data()
```

This will return data in the following format -
```
{'Likes': {u'canvasondemand': 1988, u'cafepress': 7466}, 'Page Load': {u'canvasondemand': 450, u'cafepress': 1661}}
```

So, it returns the values of the metrics defined segregated on the `on` value.
