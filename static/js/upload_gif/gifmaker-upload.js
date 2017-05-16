var tasks = new Vue({
    el: '#main',
    data: {
        //这个属性会被传给sticker-editor
        stickers: [],
        selectClick: [],
        empty: false,
        task_count: 0,
        selected_count: 0,
        uploadInfo: '',

        editing_images: [],
        modal_data_tags: [],
        modal_data_toptags: [],

        modal_tags_toadd: [],
        modal_tags_todel: [],

        modal_toptag_toadd:[],
        modal_toptag_todel:[],

        modal_copyright: {copyright:"", hascopyright: 0},

        modal_textinfo: {textinfo: ""}
        
    },
    methods: {
    //响应 file-drop-area 的 gotfiles 事件
        addFile: function(files) {
            console.log('file');
            for (var i = 0; i < files.length; ++i) {
                var file = files[i];
                (function() {
                    var sticker = {
                        file: file,
                        selected: false,
                        textinfo: "",
                        hascopyright: 0,
                        copyright: "",
                        tag: [],
                        np_id: "",
                        hot: false,
                        toptag: []
                    };
                    
                    var reader = new FileReader();
                    reader.onload = function() {
                        console.log(reader.result)
                        sticker.store_url = reader.result;
                        tasks.stickers.push(sticker);
                        tasks.task_count = tasks.stickers.length
                    };
                    console.log(file);
                    reader.readAsDataURL(file);
                })();
            }
        }
    }
});

$(document).ready(function(){
    
    $("#id-btn-upload").on("click", function(){
        uploadFilesAction(6)
    });
    $("#id-btn-uploadonline").on("click", function(){
        uploadFilesAction(9)
    })

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
    editModalsInit()
    
})


/////////////////////以下图片编辑信息部分的代码////////////////////////////////

function editModalsInit() {
    $("#id-btn-edit-all").on("click", function(){
        editAllAction()
    });
    
    $("#id-btn-edit-tag").on("click", function(){
        editTagsAction()
    });
    $("#id-btn-edit-textinfo").on("click", function() {
        editTextinfoAction()
    })
    $("#id-btn-edit-ip").on("click", function(){
        editCopyrightAction()
    });
    $("#id-btn-remove").on("click", function(){
        delPicsAction()
    });
    $("#id-btn-sort-top").on("click", function(){
        topPicsAction()
    });
    $("#id-btn-to-hot").on("click", function(){
        addPicsToHotAction()
    });

    $("#edit-tag-modal").on('show.bs.modal', function() {
        var tagSet = new Set()
        for (var i = 0; i < tasks.editing_images.length; i++) {
            var img = tasks.editing_images[i]
            for (var j = 0; j < img.tag.length; j++) {
                tagSet.add(img.tag[j])    
            }
        }
        var tags = []
        tagSet.forEach(function(tag) {
            tags.push(tag)
        });


        tasks.modal_data_tags = tags
        tasks.modal_tags_toadd = []
        tasks.modal_tags_todel = []
        tasks.modal_toptag_toadd = []
        
    })
    $("#edit-toptag-modal").on('show.bs.modal', function() {
        var tagSet = new Set()
        var topTagSet = new Set()
        for (var i = 0; i < tasks.editing_images.length; i++) {
            var img = tasks.editing_images[i]
            for (var j = 0; j < img.tag.length; j++) {
                tagSet.add(img.tag[j])    
            }
            for (var j = 0; j < img.toptag.length; j++) {
                topTagSet.add(img.toptag[j])
            }
        }
        var tags = []
        tagSet.forEach(function(tag) {
            tags.push(tag)
        });

        var toptags = []
        topTagSet.forEach(function(tag) {
            toptags.push(tag)
        });
        tasks.modal_data_tags = tags
        tasks.modal_data_toptags = toptags
        tasks.modal_toptag_toadd = []
        tasks.modal_toptag_todel = []
    })


    $("#edit-copyright-modal").on('show.bs.modal', function() {
        tasks.modal_copyright["copyright"] = tasks.editing_images[0].copyright
        tasks.modal_copyright["hascopyright"] = tasks.editing_images[0].hascopyright
    })

    $("#edit-textinfo-modal").on('show.bs.modal', function() {
        tasks.modal_textinfo = {"textinfo":tasks.editing_images[0].textinfo}
    })

    $("#edit-all-modal").on('show.bs.modal', function() {
        var tagSet = new Set()
        for (var i = 0; i < tasks.editing_images.length; i++) {
            var img = tasks.editing_images[i]
            for (var j = 0; j < img.tag.length; j++) {
                tagSet.add(img.tag[j])    
            }
        }
        var tags = []
        tagSet.forEach(function(tag) {
            tags.push(tag)
        });

        tasks.modal_data_tags = tags
        tasks.modal_tags_toadd = []
        tasks.modal_tags_todel = []
        tasks.modal_toptag_toadd = []
        tasks.modal_copyright["copyright"] = tasks.editing_images[0].copyright
        tasks.modal_copyright["hascopyright"] = tasks.editing_images[0].hascopyright
        tasks.modal_textinfo = {"textinfo":tasks.editing_images[0].textinfo}
    })
    $("#edit-all-modal").on('hide.bs.modal', function() {
        tasks.stickers.forEach(function(sticker) {
            sticker.selected = false
        })
        tasks.selected_count = 0
    })

    setRightMenu();
}

function setRightMenu() {
    var menu = new BootstrapMenu(".sticker", {
        fetchElementData: function($elem) {
            var imageid = $elem.attr('imageid');
            var image = null
            for (var i = tasks.stickers.length - 1; i >= 0; i--) {
                var temp = tasks.stickers[i]
                if (imageid == temp.np_id) {
                    image = temp
                    break
                }
            }
            if (image != null) {
                tasks.editing_images = [image]    
            }
            return image
        },
        actionsGroups: [
            ['remove'],
            ['sortTop', 'toHot']
        ],
        actions: {
            editAll: {
                name: "总编辑",
                onClick: function(image) {
                    editAllAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
            editTag: {
                name: "编辑关键字",
                onClick: function(image) {
                    editTagsAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
            editIp: {
                name: "编辑版权",
                onClick: function(image) {
                    editCopyrightAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
            editTextinfo: {
                name: "编辑文案",
                onClick: function(image) {
                    editTextinfoAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
            remove: {
                name: "删除",
                onClick: function(image) {
                    delPicsAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
            sortTop: {
                name: "置顶",
                onClick: function(image) {
                    topPicsAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
            toHot: {
                name: "流行表情",
                onClick: function(image) {
                    addPicsToHotAction()
                },
                isEnabled: function (image) {
                    return true
                }
            },
        }
    });
}

function editAllAction() {
    checkEditingImages()
    if (tasks.editing_images.length > 0) {
        $('#edit-all-modal').modal("show")
    }
}

function editTagsAction() {
    checkEditingImages()
    if (tasks.editing_images.length > 0) {
        $('#edit-tag-modal').modal("show")
    }
}

function editCopyrightAction() {
    checkEditingImages()
    if (tasks.editing_images.length > 0) {
        $('#edit-copyright-modal').modal("show")    
    }
}

function editTextinfoAction() {
    checkEditingImages()
    if (tasks.editing_images.length > 0) {
        $('#edit-textinfo-modal').modal("show")    
    }
}

function topPicsAction() {
    checkEditingImages()
    if (tasks.editing_images.length > 0) {
        $("#edit-toptag-modal").modal("show")
    }
}

function delPicsAction() {
    deletePics()
}

function addPicsToHotAction() {
    checkEditingImages()
    if (tasks.editing_images.length > 0) {
        doAddPicsToHot()
    }
}

function checkEditingImages() {
    var temps = []
    for (var i = 0; i < tasks.stickers.length; i++) {
        var temp = tasks.stickers[i]
        if (temp.selected) {
            temps.push(temp)
        }
    }
    tasks.editing_images = temps
}
//part1:编辑modal提交时调用的函数 、实际将编辑结果作用到数据上的函数

function modalTags2Data(callback) {
    for (var j = tasks.editing_images.length - 1; j >= 0; j--) {
        var tempImage = tasks.editing_images[j]
        var tempTags = []
        if (tasks.modal_tags_todel != null && tasks.modal_tags_todel.length > 0) {
            for (var i = 0; i < tempImage.tag.length; i++) {
                var tempTag = tempImage.tag[i]
                var deleteT = false
                for (var k = 0; k < tasks.modal_tags_todel.length; k++) {
                    var tag = tasks.modal_tags_todel[k]
                    if (tempTag == tag) {
                        deleteT = true
                        break
                    }
                }
                if (!deleteT) {
                    tempTags.push(tempTag)
                }
            }
        }else {
            tempTags = tempImage.tag
        }
        if (tasks.modal_tags_toadd != null && tasks.modal_tags_toadd.length > 0) {
            tempTags = tempTags.concat(tasks.modal_tags_toadd)  
        }
        tempImage.tag = tempTags
    }
    callback(true)
}

function modalCopyright2Data(callback) {
    var copyright = tasks.modal_copyright.copyright
    var hascopyright = tasks.modal_copyright.hascopyright
    for (var j = tasks.editing_images.length - 1; j >= 0; j--) {
        var tempImage = tasks.editing_images[j]
        tempImage.hascopyright = hascopyright
        tempImage.copyright = copyright
    }
    callback(true)
}

function modalTextinfo2Data(callback) {
    var textinfo = tasks.modal_textinfo.textinfo
    for (var j = tasks.editing_images.length - 1; j >= 0; j--) {
        var tempImage = tasks.editing_images[j]
        if (tempImage.textinfo.length > 0) {
            for (var i = 0; i < tempImage.tag.length; i++) {
                var tag = tempImage.tag[i]
                tempImage.tag.splice(i, 1)
                break
            }
        }

        tempImage.textinfo = textinfo
        tempImage.tag.push(textinfo)
    }
    callback(true)
}

function modalOnline2Data(callback) {

}

function modalTopTags2Data(callback) {
    var tags = tasks.modal_toptag_toadd
    var removeTopTags = tasks.modal_toptag_todel
    for (var j = tasks.editing_images.length - 1; j >= 0; j--) {
        var tempImage = tasks.editing_images[j]
        var tempSet = new Set(tempImage.tag)
        var topSet = new Set(tempImage.toptag)
        for (var i = 0; i < tags.length; i++) {
            var tag = tags[i]
            var length1 = tempSet.size    
            tempSet.add(tag)
            var length2 = tempSet.size
            if (length1 == length2) {
                var lengthT1 = topSet.size
                topSet.add(tag)
                var lengthT2 = topSet.size
                if (lengthT1 != lengthT2) {
                    tempImage.toptag.push(tag)
                }
            }
        }

        for (var i = 0; i < removeTopTags.length; i++) {
            var tag = removeTopTags[i]
            for (var k = 0; k < tempImage.toptag.length; k++) {
                var temp = tempImage.toptag[k]
                if (temp == tag) {
                    tempImage.toptag.splice(k, 1)
                    break
                }
            }
        } 
    }
    callback(true)
}

function doAddPicsToHot() {
    for (var j = tasks.editing_images.length - 1; j >= 0; j--) {
        var tempImage = tasks.editing_images[j]
        tempImage.hot = true
        tempImage.selected = false
    }
}

function deletePics() {
    for (var j = tasks.stickers.length - 1; j >= 0; j--) {
        var temp = tasks.stickers[j]
        if (temp.selected) {
            tasks.stickers.splice(j, 1)    
        }
    }
    tasks.task_count = tasks.stickers.length
    tasks.selected_count = 0
}


/////////////////////^^^^^^^^^^^^^^^^^^^^^^^^^^^^////////////////////////////////

function uploadFilesAction(level) {
    waitingDialog.show('上传中...')
    var stickers = [];
    tasks.stickers.forEach(function(sticker){
        if(sticker.selected){
            stickers.push(sticker)
        }
    });
    tasks.uploadInfo = "..."
    doUploadFiles(stickers, level, function(params, data, error){
        waitingDialog.hide()
        if (error == null || error.length == 0) {
            for(var i = 0; i < tasks.stickers.length; ++i) {
                if(tasks.stickers[i].selected) {
                    tasks.stickers.splice(i--, 1);
                }
            }
            tasks.selected_count = 0
            tasks.uploadInfo = "上传成功，去处理"
        }else {
            tasks.uploadInfo = "上传失败"
            alert(error)
        }
    }) 
}

//全信息上传
function doUploadFiles(stickers, level, callback) {
    if (stickers == null || stickers.length == 0) {
        callback(null, null, "未选中需要上传的图片");
        return;
    }
    var value = []
    for (var i = 0; i < stickers.length; i++) {
        var sticker = stickers[i]
        var temp = {}
        temp["base64"] = sticker.store_url.split('base64,')[1]
        var addkw = sticker.tag
        if (addkw.length > 0) {
            temp["addkw"] = addkw    
        }
        var topkw = sticker.toptag
        if (topkw.length > 0) {
            temp["topkw"] = topkw    
        }
        temp["hascopyright"] = sticker.hascopyright
        temp["copyright"] = sticker.copyright
        temp["textinfo"] = sticker.textinfo

        if (sticker.hot) {
            temp["lv"] = 9
            temp["trendy"] = 1
        }else {
            temp["lv"] = level    
        }
        
        value.push(temp)
    }
    // console.log(JSON.stringify(value))
    var params = {
        "value" : JSON.stringify(value)
    };
    var url = DOMAIN+"/uploadpicplug";
    //提交
    _submit(url, "POST", params, callback);
}



//普通上传
function doUploadFilesffff(stickers, callback) {
    if (stickers == null || stickers.length == 0) {
        callback(null, null, "未选中需要上传的图片");
        return;
    }
    var data = new FormData();
    data.append('file_count', stickers.length);
    var count = 0;
    $.each(stickers, function(i, sticker) {
        data.append('uploadfile' + ++count, sticker.file);
    });
    var url = DOMAIN+"/uploadpic";
    //提交
    _submit_upload(url, "POST", data, callback);
}


var DOMAIN = "http://emoji.biaoqingmm.com:4567";

var _genSignature = function(url, params) {
    var names = [];
    for(var n in params){
        names.push(n);
    }

    var paramString = url
    names.sort();
    for (var nameIndex in names) {
        var key = names[nameIndex];
        var value = params[key];
        paramString += nameIndex == 0 ? '' : '&';
        paramString += key + '=' + value;
    }
    return md5(paramString).toUpperCase();
}

var _submit_upload = function(url, type, params, callback) {
    var method = type;
    if (type == null || type.length == 0) {
        method = "GET";
    };
    $.ajax({
        type: method,
        data: params,
        url: url,
        processData: false,
        contentType: false,
        success: function(data) {
            var code = data.code
            if (code == 1) {
                callback(params, data, null);
            }else {
                console.log("data" + data);
                var message = data.error;
                callback(params, null, "errorCode" + code + " " + message); 
            }
        },
        error: function(error) {
            console.log(error);
            callback(params, null, "errorCode" + error.status + " " + error.statusText);  
        },
        dataType: "json"
    });
}

var _submit = function(url, type, params, callback) {
    var method = type;
    if (type == null || type.length == 0) {
        method = "GET";
    };
    $.ajax({
        type: method,
        data: params,
        url: url,
        success: function(data) {
            var code = data.code
            if (code == 1) {
                callback(params, data, null);
            }else {
                var message = data.error;
                callback(params, null, "errorCode" + code + " " + message); 
            }
        },
        error: function(error) {
            callback(params, null, "errorCode" + error.status + " " + error.statusText);  
        },
        dataType: "json"
    });
}
