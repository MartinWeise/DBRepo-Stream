import { PanelPlugin } from '@grafana/data';
import { SimpleOptions } from './types';
import { SimplePanel } from './SimplePanel';

export const plugin = new PanelPlugin<SimpleOptions>(SimplePanel).setPanelOptions(builder => {

  const dateTime = Date.now();
  const timestamp = Math.floor((dateTime - (86400000))/1000);

  var currentdate: any = new Date();
  var oneJan: any = new Date(currentdate.getFullYear(),0,1);
  var numberOfDays = Math.floor((currentdate - oneJan) / (24 * 60 * 60 * 1000));
  var result = Math.ceil(( currentdate.getDay() + 1 + numberOfDays) / 7) - 1;

  return builder
    .addTextInput({
      path: 'query',
      name: 'Query',
      description: 'DBRepo query to make a snapshot for.',
      defaultValue: "select `time`,`value`,`component`,`stationid`,`x_coord`,`y_coord` from `data_"+String(currentdate.getFullYear()) +"_" +String(result)+"` where `time` > " + String(timestamp),
    }).addNumberInput({
      path: 'cid',
      name: 'Container ID',
      description: 'DBRepo container id.',
      defaultValue: 1,
    }).addNumberInput({
      path: 'dbid',
      name: 'Database ID',
      description: 'DBRepo database id.',
      defaultValue: 1,
    });
});
