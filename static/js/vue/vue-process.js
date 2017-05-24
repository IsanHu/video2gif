// waitingDialog.show('处理中...');
// videoList(function(data){
//     console.log(data['processed_files'])
//     tasks.processedData = data['processed_files']
//     tasks.unprocessedData = data['unprocessed_files']
// })
function addToProcess(videoName, height, tags, captionChecked, isChinese, duration, callback) {
      waitingDialog.show("添加" + videoName + "处理");
      var params = {
        "videoName": videoName,
        'height':height,
        'tags': tags,
        "captionChecked": captionChecked,
        "isChinese": isChinese,
        "duration": duration
      };
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

          // '<td>' +
          // '<p v-if="data.deleteUrl">' +
          // '<button v-bind:class="btn btn-danger delete" v-bind:data-type="data.deleteType" v-bind:data-url="data.deleteUrl">' +
          //           '<i v-bind:class="glyphicon glyphicon-trash"></i>' +
          //           '<span>删除</span>' +
          //       '</button>' + 
          // '</p>' +
          // '</td>'
          // '<td><p v-if="data.gifs_dir">' +
          //     删除
          // '</p>' +
          // '</td>' +
        '</tr>',
});

