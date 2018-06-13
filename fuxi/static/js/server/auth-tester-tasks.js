$(function () {
    $('#sampleTable').DataTable();
});

function get_target_host(nid){
    $.post('/auth-tester-tasks', {
        "task_id": nid,
        "source": "target_info"
            }, function (e) {
        document.getElementById("target_info_data").innerHTML=e;
    })
}

function delete_task(nid){
    const data = {
        "delete": nid,
    };
    swal({
      title: "Are you sure want to delete?",
      text: "",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Delete！",
      closeOnConfirm: false
    },
    function(){
        $.ajax({
            type: 'GET',
            url: '/auth-tester-tasks',
            data: data,
            success: function() {
                location.href = "/auth-tester-tasks";
                },
            error: function(xhr, type) {
            }
        });
    });
}

function rescan_task(nid){
    const data = {
        "rescan": nid,
    };
    swal({
      title: "Are you sure want to rescan?",
      text: "This will clear the scan result！",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Rescan",
      closeOnConfirm: false
    },
    function(){
        $.ajax({
            type: 'GET',
            url: '/auth-tester-tasks',
            data: data,
            success: function() {
                location.href = "/auth-tester-tasks";
                },
            error: function(xhr, type) {
            }
        });
    });
}