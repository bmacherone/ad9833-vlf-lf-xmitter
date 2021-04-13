# ad9833-vlf-lf-xmitter
![foo *bar*]

[foo *bar*]: images/xmithat.png "Schematic"

## Welcome to the Simple Alarm Server Example
This page will load and show a code example. 


<div id="code-element"></div>
<script src="https://unpkg.com/axios/dist/axios.min.js"></script>
<script>
      axios({
      method: 'get',
      url: 'https://raw.githubusercontent.com/iotify/nsim-examples/master/functional-testing/alarm-server.js'
       })
      .then(function (response) {
         document.getElementById("code-element").innerHTML = response.data;
      });
</script>


<div id="code-element"></div>
<script src="https://unpkg.com/axios/dist/axios.min.js"></script>
<script>
      axios({
      method: 'get',
      url: 'https://github.com/https://raw.githubusercontent.com/bmacherone/ad9833-vlf-lf-xmitter/src/ad9833.py'
       })
      .then(function (response) {
         document.getElementById("code-element").innerHTML = response.data;
      });
</script>

