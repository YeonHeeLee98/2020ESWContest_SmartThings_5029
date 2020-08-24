//데이터베이스에 연결
const preObject = document.getElementById('objects');

const dbRefObject = firebase.database().ref().child('objects');  //child 호출, child키 생성

//데이터 동기화
dbRefObject.on('value', snap => 
  preObject.innerText = JSON.stringify(snap.val(), null, 3));

dbRefObject.on('child_changed', snap =>{
  const liChanged = document.createElementById(snap.key);
  liChanged.innerText = snap.val()
  
});
dbRefObject.on('child_removed', snap =>{
  liChanged.innerText = snap.val()
  
});
//테이블 연결
var pageCnt = 0;
var cnt = 0;
var ary = [];
var aryLen = 0;
var rootRef = firebase.database().ref();
var ref = rootRef.child('object/guestData');

ref.orderByChild("date").startAt(3).on('value', function (snap) {
  console.log(snap.key)
  document.getElementById("answer").innerHTML = "";

  cnt = 0;

  ary = [];
  snap.forEach(function (child) {
    var childData = child.val();
    var carNum = childData.carNum;
    var date = childData.date;
    var time = childData.time;

    cnt++;
    ary.push(childData);
  });
  loadData();
  console.log(ary.length);
});  


function loadData(params) {
  var limit = ary.length;
  if (limit > 10) {
    limit = 10;
  }
  $('#answer').empty();
  if (ary.length == 0) return false;
  var str = '';
  for (var i = 0; i < limit; i++) {
    if (ary.length > i) {
      str += '<tr class= "bodys">'
      str += "<td ></td><td>" + ary[i].carNum + "</td><td> " + ary[i].time + "</td><td>" + ary[i].date + "</td></tr>"
    }
    str += '</tr>';
  }
  $('#answer').append(str);
  paging();
  body();
}

function body() {
  $('.bodys').off().click(function () {

    var idx = $(this).index();
    idx = (pageCnt - 1) * 10 + idx;
    
    //var date = ary[idx].date;
    //var time = ary[idx].time;

    //storage(): 버킷의 루트 
    var storage = firebase.storage();
    var storageRef = firebase.storage().ref();
    var imagesRef = storageRef.child('images');
    var fileName = ary[idx].carNum + '.jpg';
    
    var spaceRef = storageRef.child('images/' + fileName + '');

    storageRef.child('images/' + fileName + '').getDownloadURL().then(function (url) {
      window.open(url);
      console.log(fileName);
    }).catch(function (error) {
      switch (error.code) {
        case 'storage/object-not-found':
          // 파일이 존재하지 않을 때
          break;

        case 'storage/unauthorized':
          // 파일에 접근 권한이 없을 시
          break;

        case 'storage/canceled':
          // 임의로 파일로드를 취소
          break;
        case 'storage/unknown':
          // 기타 에러
          break;
      }
    });
  })
}


function paging(params) {
  var str = '';
  var page = ary.length / 10;
  if (ary.length % 10 > 0)
    page = page + 1;
  page = parseInt(page);
  $('#aaa').empty();
  str += '페이지'
  for (var i = 1; i < page + 1; i++) {
    str += '<a class = "page" style="cursor: pointer; padding: 5px 10px;">' + i + '</a>';
  }
  $('#aaa').append(str);
  setTimeout(function () { pageing(); }, 100);

}

function pageing() {
  $('.page').off().click(function () {
    var idx = $(this).index();

    var count = $('#aaa a:eq(' + idx + ')').html();
    count = parseInt(count);
    pageCnt = count;
    //class css가 안먹혀서 css 추가
    $('#aaa a').css('color', '');
    $('#aaa a:eq(' + idx + ')').css('color', '#FFF');
    // class 제거
    $('#aaa a').removeClass("pageActive");
    // 선택된 페이지 번호에 css 추가
    $('#aaa a:eq(' + idx + ')').addClass("pageActive");
    var start = (count * 10) - 10;
    $('#answer').empty();
    var str = '';
    var finish = start + 10;
    var limit = ary.length;
    for (var i = start; i < finish; i++) {
      if (limit > i) {
        str += '<tr class= "bodys">'
        str += "<td ></td><td>" + ary[i].carNum + "</td><td> " + ary[i].time + "</td><td>" + ary[i].date + "</td></tr>"
      }
      else {
        break;
      }
      str += '</tr>';
    }
    $('#answer').append(str);
    //paging();
    body();

  });
}

