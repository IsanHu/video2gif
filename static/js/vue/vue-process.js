//搜索
function search() {
      key = $("#searchInput").val().trim();
      if (key.length == 0) {
        alert("请输入搜索词");
        return;
      }
      getVidesWithPage(1)
  }
  

//分页逻辑
function getVidesWithPage(page) {
      waitingDialog.show("加载中...");
      key = $("#searchInput").val().trim();
      var params = {
        "page": page,
        "key": key,
      };
      console.log(params)
      url = "/videos"
      $.ajax({
          type: "POST",
          data: params,
          url: url,
          success: function(data) {
              waitingDialog.hide();
              console.log("成功");
              tasks.videos = data.videos;
              tasks.current_page = data.current_page;
              tasks.page_indexs = data.page_indexs;
          },
          error: function(data) {
              waitingDialog.hide();
          },
          dataType: "json"
      });
  }

function nextPageButtonClicked() {
    var currentPage = tasks.current_page
    var pageIndexs = tasks.page_indexs
    var pageCount = pageIndexs.length
    if (currentPage < pageCount) {
        getVidesWithPage(currentPage + 1);
    }else{
    }
}

function prePageButtonClicked() {
    var currentPage = tasks.current_page
    var pageIndexs = tasks.page_indexs
    var pageCount = pageIndexs.length
    if (currentPage > 1) {
        getVidesWithPage(currentPage - 1);
    }else{
    }
}


//处理逻辑
function addToProcessButtonClicked() {
  var readbleName = $('#videoToProcess').text()
  var videoName = $('#hashName').text()
  var tagString = $("#tag").val().trim();
  var tags = $("#tag").val().trim().split("\n");
  captionChecked = $("#captionCheckbox").prop('checked')

  duration = 0
  isChinese = false
  if (captionChecked == true) {
    isChinese = $("#chinese").prop('checked')
  }else{
    var duration_str = $("#duration").val()
    duration = parseInt(duration_str)
      if (isNaN(duration) || duration < 1 || duration > 5) {
        alert("请填写符合要求的时间间隔")
        return
      }
  }

  var height = 0
  height_str = $("#img-height").val()
  if (height_str != "") {
      height = parseInt(height_str)
      if (isNaN(height) || height < 200 || height > 500) {
        alert("请填写符合要求的高度")
        return
      }
  }
  
  addToProcess(readbleName, videoName, height, JSON.stringify(tags), captionChecked, isChinese, duration, function(data){
      $('#addToProcessModal').modal('hide');
      if(data['result'] == 0) {
           
      }else{
        alert(data['error_message'])
      }

     video = data['video']
     if(video) {
         index = -1
         for (var i = 0; i < tasks.videos.length; i++) {
             vi = tasks.videos[i]
             if (vi['id'] == video['id']) {
                  index = i
                  break
              }
         }
         if (index >= 0) {
            Vue.set(tasks.videos, index, video)
         }
     }
  })

}

function addToProcess(readbleName, videoName, height, tags, captionChecked, isChinese, duration, callback) {
      waitingDialog.show("添加" + readbleName + "处理");
      var params = {
        "videoName": videoName,
        'height':height,
        'tags': tags,
        "captionChecked": captionChecked,
        "isChinese": isChinese,
        "duration": duration
      };
      console.log(params)
      url = "/addVideoToProcess"
      $.ajax({
          type: "POST",
          data: params,
          url: url,
          success: function(data) {
              waitingDialog.hide();
              console.log("成功");
              console.log(tasks)
              callback(data);
          },
          error: function(data) {
              waitingDialog.hide();
          },
          dataType: "json"
      });
  }



Vue.component('unprocessedtr', {
    props: ['data'],
    template: 
        '<tr>'+
          '<td>' +
          '<p>' +
          '<a v-bind:href="data.url" v-bind:download="data.name">{{data.name}}</a>' +
          '</p>' + '</td>' + 
          '<td><span class="size">{{data.size}}M</span></td>' +
          '<td>{{data.status}}</td>' +

          '<td>' +
          '<p v-if="data.op">' +
          '<button @click="process(data)">{{data.op}}</button>' + 
          '</p>' +
          '</td>' +
        '</tr>',

    methods: {
        process: function(data) {
           console.log(data.size)
           if (data.op == "处理") {
              $('#videoToProcess').text(data.name)
              $('#addToProcessModal').modal('show');
           }
        }
    }, 
});

Vue.component('processedtr', {
    props: ['data'],
    template: 
        '<tr>'+
          '<td>' +
          '<p>' +
          '<a v-bind:href="data.url" v-bind:download="data.name">{{data.name}}</a>' +
          '</p>' + '</td>' + 
          '<td><span class="size">{{data.size}}M</span></td>' +
          '<td>' +
          '<p v-if="data.gifs_dir">' +
          '<a v-bind:href="data.gifs_dir" target="_blank">{{data.gif_count}}张</a>' +
          '</p>' + '</td>' +
          '<td>' +
          '<p v-if="data.ziped_gif_info">' +
          '<a v-bind:href="data.ziped_gif_info.url" target="_blank">原尺寸图{{data.ziped_gif_info.size}}M</a>' +
          '</p>' + '</td>' +

        '</tr>',
});


Vue.component('videos', {
    props: ['data'],
    template: 
        '<tr>'+
          '<td>{{data.name}}</td>'+
          '<td>{{data.video_info.dimention}}({{data.video_info.duration}})</td>'+
          '<td>{{data.video_info.size}}</td>'+
          '<td>{{data.upload_time}}</td>'+
          '<td>' +
             '<p v-if="data.status == 0">' +
                '<button class="btn btn-default" @click="processVideo">处理</button>' +
          '</p>' +

          '<p v-else-if="data.status == 1">' +
              '<a v-bind:href="data.gif_info.gifs_dir" target="_blank">{{data.gif_info.gif_count}}张</a>' + 
              '&nbsp &nbsp' +
              '<a v-bind:href="data.ziped_gif_info.download_url" target="_blank">原尺寸图{{data.ziped_gif_info.size}}</a>' +
              '&nbsp &nbsp' +
              '<button class="btn btn-danger" style="float: right;" @click="deleteProcessed">删除</button>' +
          '</p>' +
          '<p v-else>' +
              '{{data.status_info}}' + 
          '</p>' +
          '</td>' +
        '</tr>',

    methods: {
        deleteProcessed: function() {
            console.log("删除已经处理过的")
            console.log(this.data.name)

        },

        processVideo: function() {
            console.log("处理:")
            console.log(this.data.name)
            $('#videoToProcess').text(this.data.name)
            $('#hashName').text(this.data.hash_name)
            $('#addToProcessModal').modal('show');

        }
    }, 
});

Vue.component('pageindex', {
    props: ['p_index', 'current_page'],
    template: 
        '<li v-if="p_index == current_page" v-bind:pageIndex="p_index" class="active pageIndexButton" @click="gotoPage(p_index)"><a>{{ p_index }}</a></li>' +
        '<li v-else v-bind:pageIndex="p_index" class="pageIndexButton" @click="gotoPage(p_index)"><a>{{ p_index }}</a></li>',
    methods: {
        gotoPage: function(page) {
            getVidesWithPage(page)
        },
    }, 
});

