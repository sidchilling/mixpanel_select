# This script is used for selecting from mixpanel. 

import mixpanel

# The map that will drive everything
# Description of the fields -
# from_date : datetime object from which data has to be retrieved
# to_date : datetime object to which data has to be retrived
# on: group by - has to be present
# where : to form the where condition - if a condition value list has one more than one value 
# then it is ORed and all the attrs are ANDed
# events : the list of events to be retrieved

class MixpanelSelect(object):

    def __init__(self, mixpanel_api_key, mixpanel_api_secret, global_map):
	assert mixpanel_api_key and mixpanel_api_secret and global_map, 'missing args'
	self.mixpanel_api_key = mixpanel_api_key
	self.mixpanel_api_secret = mixpanel_api_secret
	self.global_map = global_map

    def _make_single_where(self, attr_name, values):
	where = ''
	if len(values) > 0:
	    where = '('
	    for value in values:
		if len(where) > 1:
		    where = '%s or "%s" == properties["%s"]' %(where, value, attr_name)
		else:
		    where = '%s"%s" == properties["%s"]' %(where, value, attr_name)
	    where = '%s)' %(where)
	return where

    def _make_where_from_where_map(self, exp, m):
	for where_name in m.keys():
	    single_where = self._make_single_where(attr_name = where_name,
		    values = m.get(where_name))
	    if len(single_where) > 0:
		if len(exp) > 0:
		    exp = '%s and %s' %(exp, single_where)
		else:
		    exp = single_where
	return exp

    def _make_where_exp(self, where, event_where):
	exp = ''
	exp = self._make_where_from_where_map(exp = exp, m = where)
	exp = self._make_where_from_where_map(exp = exp, m = event_where)
	return exp

    def _make_mixpanel_connection(self):
	mixpanel_connection = mixpanel.Mixpanel(self.mixpanel_api_key, self.mixpanel_api_secret)
	return mixpanel_connection

    def _fetch_mixpanel_data(self, method, **kwargs):
	data = {}
	try:
	    mixpanel_obj = self._make_mixpanel_connection()
	    data = mixpanel_obj.request(method, kwargs)
	except Exception as e:
	    log.exception('exception while fetching data from mixpanel. e: %s' %(e))
	return data

    def _get_segmented_data(self, event_name, type, from_date, to_date, where, on):
	return self._fetch_mixpanel_data(['segmentation'], event = event_name, 
		from_date = from_date.strftime('%Y-%m-%d'),
		to_date = to_date.strftime('%Y-%m-%d'),
		where = where, unit = 'month', type = type, 
		on = 'properties["%s"]' %(on))

    def _get_data_sum(self, values):
	total = 0
	for dates in values:
	    total = total + values.get(dates)
	return total
	
    def _get_event_res(self, m, where, from_date, to_date, on):
	where = self._make_where_exp(where = where, event_where = m.get('where', {}))
	segmented_data = self._get_segmented_data(event_name = m.get('event_name'), type = m.get('type'),
		from_date = from_date, to_date = to_date, where = where, on = on)
	# Event level aggregation
	res = {}
	for on_key in segmented_data.get('data', {}).get('values', {}):
	    res[on_key] = self._get_data_sum(values = segmented_data.get('data').get('values').get(on_key))
	return res

    def _get_metric_res(self, metric, metric_event_list, where, from_date, to_date, on):
	res = {}
	for event_map in metric_event_list:
	    event_res = self._get_event_res(m = event_map, where = where, from_date = from_date,
		    to_date = to_date, on = on)
	    # Metric level aggregation
	    for on_key in event_res:
		if on_key in res:
		    res[on_key] = res.get(on_key) + event_res.get(on_key)
		else:
		    res[on_key] = event_res.get(on_key)
	return res

    def get_data(self):
	res = {}
	for metric in self.global_map.get('metrics', {}).keys():
	    metric_res = self._get_metric_res(metric = metric, 
		    metric_event_list = self.global_map.get('metrics').get(metric), 
		    where = self.global_map.get('where'),
		    from_date = self.global_map.get('from_date'), 
		    to_date = self.global_map.get('to_date'),
		    on = self.global_map.get('on'))
	    # Map level aggregation
	    if metric not in res:
		res[metric] = {}
	    for on_key in metric_res:
		if on_key in res.get(metric):
		    res[metric][on_key] = res.get(metric).get(on_key) + metric_res.get(on_key)
		else:
		    res[metric][on_key] = metric_res.get(on_key)
	return res
