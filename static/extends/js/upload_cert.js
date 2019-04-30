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

function run_waitMe(text) {
    $('body').waitMe({
        effect: 'win8_linear',
        text: text,
        bg: 'rgba(255,255,255,0.7)',
        color: '#000',
        sizeW: '',
        sizeH: '',
    });
}


function upload_cert_ajax(messages) {
    var url = "/cert/upload_cert_page";

    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: messages,
        success: function (data) {
            // 隐藏wait效果
            $('body').waitMe('hide');

            if (data["status"] === "success") {
                swal({
                    title: "上传证书成功",
                    // text: data["message"],
                    icon: "success",
                    button: true
                })
                    .then((value) => {
                        // 清空 input 里的内容d
                        $("form input").val("");
                        $("form textarea").val("");
                    });
            } else {
                swal({
                    title: "证书上传失败",
                    text: data["message"],
                    icon: "error",
                    button: true
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("上传证书 " + textStatus + " : " + errorThrown);
        }
    });
}


// 添加域名，创建证书
function upload_cert() {
    var dns_company = $("#sel option:selected").val();
    var to_email = $("#to_email").val();
    var cc_email = $("#cc_email").val();

    var account_input = dns_company.toLowerCase();
    var api_1 = $("#" + account_input + "_key").val();
    var api_2 = $("#" + account_input + "_token").val();

    var cert_content = $("#cert_file_content").val();
    var key_content = $("#key_file_content").val();

    if (dns_company === "0") {
        toastr.error('请选择DNS解析商', 'Error', {positionClass: 'toast-top-right'});
        return false;
    }

    if (!to_email || !api_1 || !api_2 || !cert_content ||!key_content) {
        toastr.error('必填输入框中不能为空', 'Error', {positionClass: 'toast-top-right'});
        return false;
    }

    run_waitMe("Please wait...");

    var messages = {
        "dns_company": dns_company,
        "api_1": api_1,
        "api_2": api_2,
        "to_email": to_email,
        "cc_email": cc_email,
        "cert_content": cert_content,
        "key_content": key_content,
    };

    upload_cert_ajax(messages);
}