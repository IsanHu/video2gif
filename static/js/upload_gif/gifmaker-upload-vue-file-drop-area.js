Vue.component('file-drop-area', {
    template: 
    '<div class="drag-area" @drag.stop.prevent @dragstart.stop.prevent @dragend.stop.prevent="draggingOver=false" @dragover.stop.prevent="draggingOver=true" @dragenter.stop.prevent="draggingOver=true" @dragleave.stop.prevent="draggingOver=false" @drop.stop.prevent="droppedFiles" v-bind:class="{\'is-dragover\': draggingOver}">' +
        '<div class="text-center" v-bind:style="coverDiv">选择或拖放文件<span class="glyphicon glyphicon-upload"/></div>' +
        '<input type="file" name="files[]" id="file" v-bind:style="hiddenInput" @change="selectedFiles" multiple>' +
        '</input>' +
    '</div>',
    data: function() {
        return {
            draggingOver: false,
            coverDiv: {
                "left": 0,
                "line-height":"80px",
                "width":"100%",
                "position":"fixed",
                "vertical-align":"middle",
                "font-size": "18px",
                "color": "grey"
            },
            hiddenInput: {
                "width": "100%",
                "height": "80px",
                "opacity": '0',
                'text-align': "center",
                'vertical-align': "middle",
                "overflow": 'hidden',
                'z-index': '99'
            }
        };
    },
    methods: {
        droppedFiles: function(e) {
            this.$emit('gotfiles', e.dataTransfer.files);
            this.draggingOver = false;
        },
        selectedFiles: function(e){
            this.$emit('gotfiles', e.target.files);
            e.target.value='';
        }
    }
});