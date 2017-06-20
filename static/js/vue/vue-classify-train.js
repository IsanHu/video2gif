var tasks = new Vue({
    delimiters: ['${', '}'],
    el: '#task_page',
    data: {
        message: 'You loaded this page on ' + new Date(),
        stickers: [],
        current_page: 1,
        page_indexs: [],
        categoryList: ['--类别--', '暴漫', '动漫', '美食', '萌宠', '真人', '美景'],
        confidenceList:['--置信度--',0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97,0.98,0.99],
        task_count: 0,
        selected_count: 0,
        selectClick: [],

    }
  });

//搜索
function search() {
      getVidesWithPage(1)
  }
  

//分页逻辑
function getVidesWithPage(page) {
      waitingDialog.show("加载中...");

      var params = {
        "page": page,
        "category": "--类别--",
        "confidence":-1,
        "greater": 0, //是否大于设置的置信度
        "checked": -1, //是否经过人工确认 -1:不限 0：未确认 1 已确认
      };
      var category = $("#id-category-list").val();
      params['category'] = category
      

      var confidence = $("#id-confidence-list").val();
      if(confidence!="--置信度--"){
          params['confidence'] = confidence
          if($("#greater").prop('checked')) {
              params['greater'] = 1
          }else{
              params['greater'] = 0
          }
      }


      if($("#unconfirmed").prop('checked')) {
          params['checked'] = 0
      }else if($("#confirmed").prop('checked')) {
          params['checked'] = 1
      }else if($("#noneconfirm").prop('checked')) {
          params['checked'] = -1
      }

      console.log(params)
      url = "/categoryimages/images"
      $.ajax({
          type: "POST",
          data: params,
          url: url,
          success: function(data) {
              waitingDialog.hide();
              console.log("成功");

              //重置 
              tasks.selected_count = 0
              tasks.selectClick = []
              tasks.current_page = data.current_page;
              tasks.page_indexs = data.page_indexs;
              paged_stickers = []
              for (var i = 0; i < data.images.length; i++) {
                var sticker = data.images[i]
                sticker['selected'] = false
                paged_stickers.push(sticker)
              }

              tasks.stickers = paged_stickers
              tasks.task_count = paged_stickers.length
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


Vue.component('images', {
    props: ['data'],
    template: 
        '<tr>'+
          '<td><img style="max-height: 100px;" v-bind:src="data.path"></img></td>'+
          '<td>{{data.category}}</td>'+
          '<td>{{data.size}}KB</td>'+
          '<td>{{data.width}}*{{data.height}}</td>'+
          '<td>{{data.predict_info}}</td>'+
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
        '<li v-if="p_index == current_page" v-bind:pageIndex="p_index" class="active pageIndexButton"><a>{{ p_index }}</a></li>' +
        '<li v-else v-bind:pageIndex="p_index" class="pageIndexButton" @click="gotoPage(p_index)"><a>{{ p_index }}</a></li>',
    methods: {
        gotoPage: function(page) {
            getVidesWithPage(page)
        },
    }, 
});





Vue.component('sticker', {
    props: ['src'],
    template: 
      '<div @click="toggleSelection" class="thumbnail col-xs-5 col-sm-5 col-md-4 col-lg-3" v-bind:class="{\'is-selected\': src.selected}">' +
          '<img id="sticker" class="thumbnail sticker" style="width: 100%;margin-bottom:4px" v-bind:src="src.path" v-bind:imageid="src.path" ></img>' +
          '<dl>' + 
              '<dt>类别：{{src.category}} &nbsp &nbsp 置信度：{{src.confidence}}</dt>' +
              '<dt>状态：{{src.status}}</dt>' +
              '<dt>尺寸：{{src.width}}*{{src.height}} &nbsp &nbsp 文件大小: {{src.size}}KB' +
              '<dt>预测详情：{{src.predict_info}}</dt>' +
          '</dl>' +
      '</div>',
    methods: {
        toggleSelection: function(e) {
            tasks.selectClick.push(this.src)
            if (e.shiftKey) {
                var count = 0
                var last = tasks.selectClick[tasks.selectClick.length - 2]
                var current = this.src
                var start = false
                var increasing = true
                for (var i = 0; i < tasks.stickers.length; i++) {
                    var temp = tasks.stickers[i]
                    if (!start) {
                        if (temp == last) {
                            start = true
                            continue
                        }
                        if (temp == current) {
                            start = true
                            increasing = false//倒序
                        }
                    } 
                    if (start) {
                        if (!increasing) {//倒序
                            if (temp == last) {
                                break
                            }    
                        }
                        
                        temp.selected = !temp.selected
                        if (temp.selected) {
                            count++
                        } else {
                            count--
                        }
                        if (increasing) {//正序
                            if (temp == current) {
                                break
                            }    
                        }
                        
                    }                
                }
                tasks.selected_count += count
                tasks.selectClick = []
            } else {

                this.src.selected = !this.src.selected;
                if (this.src.selected) {
                    tasks.selected_count++
                } else {
                    tasks.selected_count--
                }    
            }
            
        },
    }
});

$(document).ready(function(){

    $("#id-btn-select-all").on("click", function(){
        for (var i = 0; i < tasks.stickers.length; i++) {
            var img = tasks.stickers[i]
            img.selected = true
        }
        tasks.selected_count = tasks.stickers.length
    });

    $("#id-btn-unselect-all").on("click", function(){
        for (var i = 0; i < tasks.stickers.length; i++) {
            var img = tasks.stickers[i]
            img.selected = false
        }
        tasks.selected_count = 0
    });

    $("#id-btn-reverse-select").on("click", function(){
        var count = 0
        for (var i = 0; i < tasks.stickers.length; i++) {
            var img = tasks.stickers[i]
            img.selected = !img.selected
            if (img.selected) {
                count++
            }
        }
        tasks.selected_count = count
    });

    $("#id-btn-to-confirm").on("click", function(){
      var stickerIds = [];
      tasks.stickers.forEach(function(sticker){
          if(sticker.selected){
              stickerIds.push(sticker.id)
          }
      });

      if(stickerIds.length <= 0) {
        alert("尚未选择图片")
        return
      }


      waitingDialog.show('处理中...')

      var params = {
        "image_ids": JSON.stringify(stickerIds),
      };

      console.log(params)
      url = "/categoryimages/confirm_images"
      $.ajax({
          type: "POST",
          data: params,
          url: url,
          success: function(data) {
              waitingDialog.hide();
              console.log("成功");
              if(data['result'] == 1) {
                console.log(data['message'])
              }else{
                alert(data['error_message'])
                console.log(data['error_message'])
                return
              }
              //重置 
              remain_stickers = []
              for (var i = 0; i < tasks.stickers.length; i++) {
                var sticker = tasks.stickers[i]
                if(sticker.selected == false) {
                  remain_stickers.push(sticker)
                }
              }

              tasks.stickers = remain_stickers
              tasks.task_count = remain_stickers.length
              tasks.selected_count = 0
              tasks.selectClick = []
          },
          error: function(data) {
              waitingDialog.hide();
          },
          dataType: "json"
      });
    });

    $("#id-btn-remove").on("click", function(){
      var stickerIds = [];
      tasks.stickers.forEach(function(sticker){
          if(sticker.selected){
              stickerIds.push(sticker.id)
          }
      });

      if(stickerIds.length <= 0) {
        alert("尚未选择图片")
        return
      }


      waitingDialog.show('处理中...')

      var params = {
        "image_ids": JSON.stringify(stickerIds),
      };

      console.log(params)
      url = "/categoryimages/remove_images"
      $.ajax({
          type: "POST",
          data: params,
          url: url,
          success: function(data) {
              waitingDialog.hide();
              console.log("成功");
              if(data['result'] == 1) {
                console.log(data['message'])
              }else{
                alert(data['error_message'])
                console.log(data['error_message'])
                return
              }
              //重置 
              remain_stickers = []
              for (var i = 0; i < tasks.stickers.length; i++) {
                var sticker = tasks.stickers[i]
                if(sticker.selected == false) {
                  remain_stickers.push(sticker)
                }
              }

              tasks.stickers = remain_stickers
              tasks.task_count = remain_stickers.length
              tasks.selected_count = 0
              tasks.selectClick = []
          },
          error: function(data) {
              waitingDialog.hide();
          },
          dataType: "json"
      });
    });
})



