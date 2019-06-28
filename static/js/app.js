var pyStretch = angular.module('pyStretch', []);

pyStretch.controller('logMessageCtrl', function($scope){
   var ws = new WebSocket("ws://"+document.location.hostname+":8888/websocket");


   function doMessage(obj) {
      $scope.safeApply(function () {
         $scope.msg = obj;
      });
   }

   ws.onmessage = function (evt) {
      doMessage(evt.data);
   };
});



// // 
// //    ws.send("Hello, world");
// // };
// ws.onmessage = function (evt) {
//    console.log(evt.data);
// };