import React  from 'react';
import { PanelProps } from '@grafana/data';
import { SimpleOptions } from 'types';
import { css, cx } from 'emotion';
import { stylesFactory } from '@grafana/ui';

interface Props extends PanelProps<SimpleOptions> {}


export const SimplePanel: React.FC<Props> = ({ options, data, width, height }) => {
  
  const styles = getStyles();
  const [qid, setQid] = React.useState('');

  const snapshot = () => {
    fetch(`http://s125.dl.hpc.tuwien.ac.at:8000/${options.cid}/${options.dbid}`, {
      method: 'POST',
      body: getTimestampQuery()
    }).then(res => res.text()).then(text => {
      setQid(text)
  })};

  return (

    <div className={cx(styles.wrapper,css`width: ${width}px; height: ${height}px;`)}>

      <div className={cx(styles.row)}>
      <button className={cx(styles.button)} onClick={snapshot}>
        Take Snapshot
      </button> 

      <div className={styles.textBox}>  
        {qid !== '' ? 
        (<div className={cx(css`font-size: 1.3em;`)}> Persistent Identifier: <a className={cx(styles.link)} href={qid}>{qid}</a> </div>) : 
        (<div>
          <a className={cx(css`font-size: 1.2em;`)}>This button creates a persistent identifier (snapshot) for following query (24-hour data):</a>
          <br></br>
          <i className={cx(css`font-size: 0.9em;color:#AF4F19;`)}>{getTimestampQuery()}</i>
        </div>
        )}
      </div>
      </div>
    </div>
  );
};

const getTimestampQuery = () => {

  const dateTime = Date.now();
  const timestamp = Math.floor((dateTime - (86400000))/1000);

  var currentdate: any = new Date();
  var oneJan: any = new Date(currentdate.getFullYear(),0,1);
  var numberOfDays = Math.floor((currentdate - oneJan) / (24 * 60 * 60 * 1000));
  var result = Math.ceil(( currentdate.getDay() + 1 + numberOfDays) / 7) - 1;

  return "SELECT `time`,`value`,`component`,`stationid`,`x_coord`,`y_coord` FROM `data_"+String(currentdate.getFullYear()) +"_" +String(result)+"` WHERE `time` > " + String(timestamp)
}


const getStyles = stylesFactory(() => {
  return {
    wrapper: css`
      display: flex;
      align-items: center;
      justify-content: center;
    `,
    row: css`
    display: flex;
    flex-direction: column;
  `,
    link: css`
      color:#3E7DBB;
      text-decoration:underline;
    `,
    button: css`
      padding:10px;
      color:white;
      font-size:1.2em;
      background-color:#E34213;
      border-radius:5px;
      border:none;

    `,
    textBox: css`
      padding: 10px;
      text-align: center;
    `,
  };
});
