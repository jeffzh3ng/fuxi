$(function () {
    $('#sampleTable').DataTable();
    $(".new-scan").click(function () {
        const task_name = $('[name="task_name"]').val();
        const target_addr = $('[name="target_addr"]').val();
        const scan_type = $('[name="scan_type"]').val();
        const description_val = $('[name="description_val"]').val();
        if (!task_name || !target_addr || !scan_type) {
            swal("Warning", "Please check the input!", "error");
        } else {
            $.post('/acunetix-scanner', {
                "task_name": task_name,
                "target_addr": target_addr,
                "scan_type": scan_type,
                "description_val": description_val,
                "source": "new_scan"
            }, function (e) {
                if (e === 'success') {
                    swal({
                            title: "Task added successfully!",
                            text: "",
                            type: "success",
                            confirmButtonColor: "#41b883",
                            confirmButtonText: "ok",
                            closeOnConfirm: false
                        },
                        function () {
                            location.href = "/acunetix-scanner";
                        });
                } else {
                    swal("Error", "Something wrong", "error");
                }
            })
        }
    });
});

function delete_scan(nid){
    swal({
      title: "Are you sure want to delete?",
      text: "",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Delete！",
      closeOnConfirm: false
    },
    function() {
        $.post('/acunetix-tasks', {
            "delete": nid,
            "source": 'delete_scan',
        }, function (e) {
            if (e === 'success') {
                swal({
                        title: "Delete Success",
                        text: "",
                        type: "success",
                        confirmButtonColor: "#41b883",
                        confirmButtonText: "ok",
                        closeOnConfirm: false
                    },
                    function () {
                        location.href = "/acunetix-tasks";
                    });
            } else {
                swal("Error", "Something wrong", "error");
            }
        })
    })
}

function report_url(nid){
    $.post('/acunetix-tasks', {
        "scan_id": nid,
        "source": 'report',
    }, function (e) {
        if (e !== 'warning') {
            document.getElementById("report_download_html").innerHTML="<a href=\"static/download/" + e['html_url'] + "\" target=\"view_window\"><button class=\"btn btn-primary btn-block\" type=\"button\">HTML</button></a>";
            document.getElementById("report_download_pdf").innerHTML="<a href=\"static/download/" + e['pdf_url'] + "\" target=\"view_window\"><button class=\"btn btn-primary btn-block\" type=\"button\">PDF</button></a>";
        }
    })
}

function delete_task(nid){
    swal({
      title: "Are you sure want to delete?",
      text: "",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Delete！",
      closeOnConfirm: false
    },
    function() {
        $.post('/acunetix-scanner', {
            "delete": nid,
            "source": 'delete_task',
        }, function (e) {
            if (e === 'success') {
                swal({
                        title: "Delete Success",
                        text: "",
                        type: "success",
                        confirmButtonColor: "#41b883",
                        confirmButtonText: "ok",
                        closeOnConfirm: false
                    },
                    function () {
                        location.href = "/acunetix-scanner";
                    });
            } else {
                swal("Error", "Something wrong", "error");
            }
        })
    })
}

function down_report(nid){
    $.post('/acunetix-scanner', {
        "task_id": nid,
        "source": 'download_report',
    }, function (e) {
        if (e !== 'warning') {
            document.getElementById("report_download_html").innerHTML="<a href=\"static/download/" + e['html_url'] + "\" target=\"view_window\"><button class=\"btn btn-primary btn-block\" type=\"button\">HTML</button></a>";
            document.getElementById("report_download_pdf").innerHTML="<a href=\"static/download/" + e['pdf_url'] + "\" target=\"view_window\"><button class=\"btn btn-primary btn-block\" type=\"button\">PDF</button></a>";
        }
    })
}