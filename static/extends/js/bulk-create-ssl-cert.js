// 解决在使用js的ajax后，提交表单时出现Forbidden (CSRF token missing or incorrect.)问题
$(function () {
    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });
});

// getCookie函数
function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");

    if (arr = document.cookie.match(reg))
        return unescape(arr[2]);
    else
        return null;
}


function bulkCreateSLLCert() {
    var bulk_messages = $("#bulkMessages").val();
    var lines = bulk_messages.split("\n").length;

    var limitLines = 100;
    if (lines > limitLines) {
        toastr.error("已超过行数限制", "Error", {positionClass: 'toast-top-right'});
        return false
    }

    if (!bulk_messages) {
        return false
    }

    var url = "/cert/bulk_create_cert_page";
    var msg = {
        "bulk_messages": bulk_messages,
    };

    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: msg,
        success: function (data) {
            if (data === "success") {
                toastr.success('已提交,证书创建中...', 'Success', {positionClass: 'toast-top-right'});
            } else {
                toastr.error('批量创建失败,请检查', 'Error', {positionClass: 'toast-top-right'});
            }

        },
        error: function (data, textStatus, errorThrown) {
            alert("bulk create ssl cert " + textStatus + " : " + errorThrown);
        }
    })

}