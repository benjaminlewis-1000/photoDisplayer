
aa =' [{"criteriaType":"Person","booleanValue":"is","criteriaVal":"Aaron Swenson"}]'

aa = '[{"criteriaType":"Person","booleanValue":"is","criteriaVal":"Aaron Swenson"},{"criteriaType":"Year","booleanValue":"is","criteriaVal":"2017"},{"criteriaType":"Date Range","booleanValue":"2018/02/07","criteriaVal":"None"},{"criteriaType":"Month","booleanValue":"is","criteriaVal":"9"},{"criteriaType":"Year", "booleanValue": "is before", "criteriaVal": "2018"}, {"criteriaType":"Year", "booleanValue": "is after", "criteriaVal": "2010"}]'

import queryMaker


qq = queryMaker.QueryMaker('/home/pi/phdisp/config/params.xml')

qq.buildQueryFromJSON(aa)
