Vue.component('sticker', {
    props: ['src'],
    template: 
      '<div @click="toggleSelection" class="thumbnail col-xs-5 col-sm-5 col-md-4 col-lg-3" v-bind:class="{\'is-selected\': src.selected}">' +
          '<img v-if="src.download_failed" id="sticker" @click="reloadClick(src)" class="thumbnail sticker" style="width: 100%;margin-bottom:4px" src="http://mgc.biaoqingmm.com:5003/static/img/loading.gif" v-bind:imageid="src.np_id" ></img>' +
          '<img v-else id="sticker" class="thumbnail sticker" style="width: 100%;margin-bottom:4px" v-bind:src="src.store_url" v-bind:imageid="src.np_id" ></img>' +
          '<dl>' + 
              '<dt>编号：{{src.gif_info.index}}  图片大小：{{src.gif_info.size}}KB</dt>' +
              '<dt v-if="src.hot" style="color:#f0ad4e;font-size:18px;">流行表情(直接上线)</dt>' +
              '<dt>关键字：</dt>' +
              '<dd>' +  
                  '<span v-for="tag in src.tag" style="padding-right: 10px;">{{tag}}</span>' +
              '</dd>' +
              '<dt>文案：</dt>' +
              '<dd >{{src.textinfo}}</dd>' +
              
              '<dt v-if="src.toptag.length>0">置顶关键字：</dt>' + 
              '<dd>' +
                    '<span v-for="tag in src.toptag" style="padding-right: 10px;">{{tag}}</span>' +
              '</dd>' +
              '<dt>版权：</dt>' +
              '<dd>{{src.copyright}}</dd>' + 
              '<dt><a style="float: right" v-bind:href="src.original_url" v-bind:download="src.gif_info.name">下载原图（{{src.gif_info.full_size}}MB）</a></dt>' +
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

        reloadClick: function(sticker) {
            downloadSticker(tasks.current_page, sticker)
        }
    }
});

Vue.component('tagedittaghas', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-default" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleTopEdit" class="btn btn-default" style="top: 1px" type="button" >置顶</button>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleEdit" class="btn btn-default glyphicon glyphicon-remove" style="top: 1px" type="button" ></button>' +
            '</span>' +
            
        '</div>',
    methods: {
        toggleEdit: function() {
            for (var i = 0; i < tasks.modal_data_tags.length; i++) {
                var temp = tasks.modal_data_tags[i]
                if (temp == this.tag) {
                    tasks.modal_data_tags.splice(i, 1)
                    break
                }
            }
            tasks.modal_tags_todel.push(this.tag)
        },
        toggleTopEdit: function() {
            tasks.modal_toptag_toadd.push(this.tag)
        }

    }
});

Vue.component('tagedittagadd', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-success" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleTopEdit" class="btn btn-success" style="top: 1px" type="button" >置顶</button>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="removeButtonClick" class="btn btn-success glyphicon glyphicon-remove" style="top: 1px" type="button" ></button>' +
            '</span>' +
        '</div>',
    methods: {
        removeButtonClick: function() {
            for (var i = 0; i < tasks.modal_tags_toadd.length; i++) {
                var temp = tasks.modal_tags_toadd[i]
                if (this.tag == temp) {
                    tasks.modal_tags_toadd.splice(i, 1)
                    return
                }
            }
        },
        toggleTopEdit: function() {
            tasks.modal_toptag_toadd.push(this.tag)
        }
    }
});

Vue.component('tagedittagdelete', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-danger" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="removeButtonClick" class="btn btn-danger glyphicon glyphicon-remove" style="top: 1px" type="button" ></button>' +
            '</span>' +
        '</div>',
    methods: {
        removeButtonClick: function() {
            for (var i = 0; i < tasks.modal_tags_todel.length; i++) {
                var temp = tasks.modal_tags_todel[i]
                if (this.tag == temp) {
                    tasks.modal_tags_todel.splice(i, 1)
                    break
                }
            }
            tasks.modal_data_tags.push(this.tag)
        }
    }
});

Vue.component('taginput', {
    props: [],
    data: function() {
        var dic = {
            tag: ""
        }
        return dic
    },
    template: 
        '<div class="navbar-form" style="padding-left: 0px">' +
            '<div class="form-group" style="margin-right: 10px">' +
                '<input type="text" @keydown="inputKeydownAction" class="form-control" placeholder="关键词" v-model="tag"/>' +
            '</div>' +
            '<button @click="toggleAddTag" class="btn btn-primary" type="button" style="margin-right: 10px">添加</button>' +
            '<button @click="deleteAllTag" class="btn btn-primary" type="button">全部删除</button>' +
        '</div>',
    methods: {
        toggleAddTag: function() {
            if (this.tag.length > 0) {
                tasks.modal_tags_toadd.push(this.tag)
                this.tag = ""    
            }
        },
        inputKeydownAction: function(e) {
            if (e.keyCode == 13) {
                e.preventDefault();
                if (this.tag.length > 0) {
                    tasks.modal_tags_toadd.push(this.tag)
                    this.tag = ""    
                }
            }
        },
        deleteAllTag: function() {
            tasks.modal_tags_todel = tasks.modal_tags_todel.concat(tasks.modal_data_tags)
            tasks.modal_data_tags = []
        }
    }, 
});

Vue.component('tagsubmit', {
    props: [],
    template: 
        '<div>' +
            '<button type="button" class="btn btn-default" data-dismiss="modal">' +
                '关闭' +
            '</button>' +
            '<button @click="toggleTagSubmit" id="id-btn-edit-tag-submit" type="button" class="btn btn-primary">' +
                '提交更改' +
            '</button>' +
        '</div>',
    methods: {
        toggleTagSubmit: function() {
            modalTags2Data(function(flag) {
                if (flag) {
                    modalTopTags2Data(function(flag) {
                        if (flag) {
                            $('#edit-tag-modal').modal("hide")
                        }
                    })
                }
            })
        }
    }, 
});

Vue.component('copyrightmodalbody', {
    props: ["cro"],
    template: 
        '<form>' +
            '<div style="margin-left: 20px">' +
                '<div class="radio">' +
                    '<label style="font-size: 16px"><input type="radio" name="cr" value=1 v-model="cro.hascopyright"/>有版权无争议</label>' +
                '</div>' +
                '<div class="form-inline">' +
                    '<span style="font-size: 16px">版权方：</span>' +
                    '<input type="text" class="form-control" v-bind:disabled="cro.hascopyright!=1" style="font-size: 16px" v-model="cro.copyright"/> ' +
                '</div>' +
                '<div class="radio">' +
                    '<label style="font-size: 16px"><input type="radio" name="cr" value=0 v-model="cro.hascopyright"/>无版权无争议</label>' +
                '</div>' +
                '<div class="radio">' +
                    '<label style="font-size: 16px"><input type="radio" name="cr" value=-1 v-model="cro.hascopyright"/>无版权有争议</label>' +
                '</div>' +
            '</div>' +
        '</form>',
    methods: {

    }
});

Vue.component('copyrightsubmit', {
    props: [],
    template: 
        '<div>' +
            '<button type="button" class="btn btn-default" data-dismiss="modal">' +
                '取消' +
            '</button>' +
            '<button @click="toggleCopyrightSubmit" type="button" class="btn btn-primary">' +
                '保存' +
            '</button>' +
        '</div>',
    methods: {
        toggleCopyrightSubmit: function() {
            modalCopyright2Data(function(flag) {
                if (flag) {
                    $('#edit-copyright-modal').modal("hide")
                }
            })
        }
    }
});

Vue.component('textinfomodal', {
    props: ["src"],
    template: 
        '<div>' +
            '<div class="form-group" style="margin-right: 10px">' + 
                '<input type="text" class="form-control" placeholder="文案" v-model="src.textinfo"/>' +                     
            '</div>' +
        '</div>',
    methods: {
    }
});

Vue.component('textinfosubmit', {
    props: ["src"],
    template: 
        '<div>' +
            '<button type="button" class="btn btn-default" data-dismiss="modal">' +
                '取消' +
            '</button>' +
            '<button @click="toggleTextInfoSubmit" type="button" class="btn btn-primary">' +
                '保存' +
            '</button>' +
        '</div>',
    methods: {
        toggleTextInfoSubmit: function() {
            modalTextinfo2Data(function(flag) {
                if (flag) {
                    $('#edit-textinfo-modal').modal("hide")
                }
            })
        }
    }
});


Vue.component('taggrouptaghas', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-default" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleTopEdit" class="btn btn-default glyphicon glyphicon-ok" style="top: 1px" type="button" ></button>' +
            '</span>' +
        '</div>',
    methods: {
        toggleTopEdit: function() {
            tasks.modal_toptag_toadd.push(this.tag)
        }
    }
});

Vue.component('taggrouptophas', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-warning" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleTopEditDelete" class="btn btn-default" style="top: 1px" type="button" >去除置顶</button>' +
            '</span>' +
        '</div>',
    methods: {
        toggleTopEditDelete: function() {
            tasks.modal_toptag_todel.push(this.tag)
        }
    }
});

Vue.component('taggrouptopdelete', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-danger" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleTopEditDelete" class="btn btn-danger glyphicon glyphicon-remove" style="top: 1px" type="button" ></button>' +
            '</span>' +
        '</div>',
    methods: {
        toggleTopEditDelete: function() {
            for (var i = 0; i < tasks.modal_toptag_todel.length; i++) {
                var temp = tasks.modal_toptag_todel[i]
                if (this.tag == temp) {
                    tasks.modal_toptag_todel.splice(i, 1)
                    return
                }
            }
        }
    }
});

Vue.component('taggrouptopadd', {
    props: ['tag'],
    template: 
        '<div class="input-group" style="display: inline-block;margin: 5px">' +
            '<span class="input-group-btn" >' +
                  '<div class="btn btn-warning" style="top: 1px">{{tag}}</div>' +
            '</span>' +
            '<span class="input-group-btn">' +
                  '<button @click="toggleAddToTop" class="btn btn-warning glyphicon glyphicon-remove" style="top: 1px" type="button" ></button>' +
            '</span>' +
        '</div>',
    methods: {
        toggleAddToTop: function() {
            for (var i = 0; i < tasks.modal_toptag_toadd.length; i++) {
                var temp = tasks.modal_toptag_toadd[i]
                if (this.tag == temp) {
                    tasks.modal_toptag_toadd.splice(i, 1)
                    return
                }
            }
        }
    }
});

Vue.component('toptagsubmit', {
    props: [],
    template: 
        '<div>' +
            '<button type="button" class="btn btn-default" data-dismiss="modal">' +
                '关闭' +
            '</button>' +
            '<button @click="toggleTopTagsSubmit" type="button" class="btn btn-primary">' +
                '保存' +
            '</button>' +
        '</div>',
    methods: {
        toggleTopTagsSubmit: function() {
            modalTopTags2Data(function(flag) {
                if (flag) {
                    $('#edit-toptag-modal').modal("hide")
                }
            })
        }
    }, 
});

Vue.component('allsubmit', {
    props: [],
    template: 
        '<div>' +
            '<button type="button" class="btn btn-default" data-dismiss="modal">' +
                '关闭' +
            '</button>' +
            '<button @click="toggleAllSubmit" type="button" class="btn btn-primary">' +
                '保存' +
            '</button>' +
        '</div>',
    methods: {
        toggleAllSubmit: function() {
            
            modalTags2Data(function(flag) {
                if (flag) {
                    modalTopTags2Data(function(flag) {
                        if (flag) {
                            if (tasks.modal_copyright.hascopyright != 1) {
                                tasks.modal_copyright.copyright = ""
                            }
                            modalCopyright2Data(function(flag) {
                                if (flag) {
                                    if (tasks.modal_textinfo.textinfo == null) {
                                        tasks.modal_textinfo.textinfo = ""
                                    }
                                    modalTextinfo2Data(function(flag) {
                                        if (flag) {
                                            $('#edit-all-modal').modal("hide")
                                        }
                                    })
                                }
                            })
                        }
                    })
                }
            })            
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
            downloadPagedStickers(page)
        },
    }, 
});


//下载逻辑
function downloadPagedStickers(page) {
    //重置 
    tasks.current_page = page
    new_page_indexs = []
    for (var i = 1; i <= tasks.page_count; i++) {
        new_page_indexs.push(i)
    }
    tasks.page_indexs = new_page_indexs


    tasks.stickers = tasks.paged_stickers[page - 1].stickers
    tasks.task_count = tasks.stickers.length

    if(tasks.paged_stickers[page - 1].download == 1) {
        console.log("已下载过，不需要重新下载")
        return
    }
    tasks.paged_stickers[page - 1].download = 1
    for (var i = 0; i < tasks.paged_stickers[page - 1].stickers.length; i++) {
        sticker = tasks.paged_stickers[page - 1].stickers[i]
        downloadSticker(page, sticker)
    }
}

function downloadSticker(page, sticker) {
    var request = new XMLHttpRequest();
    request.open('GET', sticker.url, true);
    request.responseType = 'blob';
    request.onload = function(e) {
        var reader = new FileReader();
        reader.readAsDataURL(request.response);
        reader.onload =  function(e){
            sticker.store_url = e.target.result;
            index = parseInt(sticker.gif_info['index'])
            index = index - (50 * (page - 1))
            console.log("记录的index:")
            console.log(index)

            var temp_sticker = {
                    selected: sticker.selected,
                    textinfo: sticker.textinfo,
                    name: sticker.name,
                    url: sticker.url,
                    original_url: sticker.original_url,
                    hascopyright: sticker.hascopyright,
                    copyright: sticker.copyright,
                    tag: sticker.tag,
                    np_id: sticker.np_id,
                    hot: sticker.hot,
                    toptag: sticker.toptag,
                    gif_info:sticker.gif_info,
                    store_url:sticker.store_url,
                    download_failed: false,
                };

            //检查是否是当前页
            if(page == tasks.current_page) {
                console.log("是当前页，刷新这个cell")
                Vue.set(tasks.stickers, index, temp_sticker)    
            }
            tasks.paged_stickers[page - 1].stickers[index] = temp_sticker
        };
    };

    request.onerror = function(e) {
        console.log("下载失败")
        index = parseInt(sticker.gif_info['index'])
            index = index - (50 * (page - 1))
            console.log("记录的index:")
            console.log(index)

            var temp_sticker = {
                    selected: sticker.selected,
                    textinfo: sticker.textinfo,
                    name: sticker.name,
                    url: sticker.url,
                    original_url: sticker.original_url,
                    hascopyright: sticker.hascopyright,
                    copyright: sticker.copyright,
                    tag: sticker.tag,
                    np_id: sticker.np_id,
                    hot: sticker.hot,
                    toptag: sticker.toptag,
                    gif_info:sticker.gif_info,
                    store_url:sticker.store_url,
                    download_failed: true,
                };

            //检查是否是当前页
            if(page == tasks.current_page) {
                console.log("是当前页，刷新这个cell")
                Vue.set(tasks.stickers, index, temp_sticker)    
            }
            tasks.paged_stickers[page - 1].stickers[index] = temp_sticker
    };

    request.send();
}

//分页逻辑
function nextPageButtonClicked() {
    var currentPage = tasks.current_page
    var pageIndexs = tasks.page_indexs
    var pageCount = pageIndexs.length
    if (currentPage < pageCount) {
        downloadPagedStickers(currentPage + 1);
    }
}

function prePageButtonClicked() {
    var currentPage = tasks.current_page
    if (currentPage > 1) {
        downloadPagedStickers(currentPage - 1);
    }
}

