function delete_plugin(nid){
    const data = {
        "delete": nid,
    };
    swal({
            title: "Are you sure you want to delete?",
            text: "If you delete an item, it will be permanently lost",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Delete！",
            closeOnConfirm: false
        },
        function(){
        $.ajax({
            type: 'GET',
            url: '/plugin-management',
            data: data,
            success: function() {
                location.href = "/plugin-management";
                },
            error: function(xhr, type) {}
        });
    });
}

function plugin_info(nid){
    const data = {
        "info": nid,
    };
    $.ajax({
        type: 'GET',
        url: '/plugin-management',
        data: data,
        dataType: 'json',
        success: function(result) {
            $('#plugin_info').html(JSON.stringify(result, null, 4));
        },
        error: function(xhr, type) {

        }
    });
}

$('#sampleTable').DataTable();
Dropzone.autoDiscover = false;

$(".dropzone").dropzone({
    url: "plugin-upload",
    init: function() {
            this.on("complete", function (data) {
                const res = eval('(' + data.xhr.responseText + ')');
                if (res.result === "success") {
                    swal({
                            title: "Upload Completed",
                            text: "",
                            type: "success",
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "OK",
                            closeOnConfirm: false
                        },
                        function(){
                        location.href = "/plugin-management";
                    });
            } else {
                    swal({
                            title: "Upload Error",
                            text: "<p>Plugin Developer Guide: <a href=\"https://github.com/knownsec/Pocsuite/blob/master/docs/CODING.md\" target=\"view_window\">Pocsuite PoC </a></p>",
                            html: true,
                            type: "error",
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "OK",
                            closeOnConfirm: false
                        },
                        function(){
                        location.href = "/plugin-management";
                    });
                }
            });
        }
    });