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

// 页面加载完成之后需执行修改 "状态" 列样式
$(modify_table_style());

function modify_table_style() {
    $("table tr").find("td").each(function () {
        if ($.trim($(this).text()) === "正常") {
            $(this).css("color", "#35B34A");
        } else if ($.trim($(this).text()) === "暂停") {
            $(this).css("color", "#FF8400");
        }
    });
}


function show_modal() {
    $("#baseModalLabel").text("添加记录");
    $(".modal-body input").val("");
    $('#baseModal').modal('show');

}

function add_record() {
    run_waitMe("Please wait...");

    $('#baseModal').modal('hide');
    var top_domain = $("#top_domain").text();
    var sub_domain = $("#host_record").val();
    var record_type = $("#selectType").val();
    var line = $("#selectLine").val();
    var record_value = $("#record_value").val();
    var ttl = $("#ttl").val();
    var mx = $("#MX").val();

    var msg = {
        "top_domain": top_domain,
        // "dns_company": dns_company,
        "sub_domain": sub_domain,
        "record_type": record_type,
        "line": line,
        "record_value": record_value,
        "ttl": ttl,
        "mx": mx,
    };

    var url = "/cert/add_record/";

    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: msg,
        success: function (data) {
            $('body').waitMe('hide');

            if (data === "success") {
                swal({
                    text: sub_domain + " 已添加",
                    icon: "success",
                    button: true
                })
                    .then((value) => {
                        // 重载页面
                        window.location.reload()
                    });

            } else {
                swal({
                    text: "添加记录失败: " + sub_domain,
                    icon: "error",
                    button: true
                });
            }
        },
        error: function (data, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("添加记录 " + "\n" + textStatus + "\n" + errorThrown);
        }
    })
}


function show_modify_modal(label) {
    $('#baseModal').modal('show');
    $("#baseModalLabel").text("修改记录");
    var tds = $(label).parent().parent();
    var old_sub_domain = tds.find("td:nth-child(1)").text();
    var record_type = tds.find("td:nth-child(2)").text();
    var record_line = tds.find("td:nth-child(3)").text();
    var record_value = tds.find("td:nth-child(4)").text();
    var ttl = tds.find("td:nth-child(5)").text();

    if (record_line === "default") {
        var record_line = "默认"
    }

    $("#host_record").val(old_sub_domain);
    $("#selectType").val(record_type);
    $("#selectLine").val(record_line);
    $("#record_value").val(record_value);
    $("#ttl").val(ttl);

    // 添加一个隐藏的input用于传旧的域名记录
    $(".modal-body").append('<input type="text" id="old_sub_domain" hidden>');
    $("#old_sub_domain").val(old_sub_domain);
    $(".modal-footer button:contains('确定')").attr("onclick", "modify_record()")
}


function modify_record() {
    run_waitMe("Please wait...");

    $('#baseModal').modal('hide');
    var top_domain = $("#top_domain").text();
    var dns_company = $("#dns_company").text();
    var old_sub_domain = $("#old_sub_domain").val();
    var new_sub_domain = $("#host_record").val();
    var record_type = $("#selectType").val();
    var line = $("#selectLine").val();
    var record_value = $("#record_value").val();
    var ttl = $("#ttl").val();
    var mx = $("#MX").val();

    var msg = {
        "top_domain": top_domain,
        "dns_company": dns_company,
        "old_sub_domain": old_sub_domain,
        "new_sub_domain": new_sub_domain,
        "record_type": record_type,
        "line": line,
        "record_value": record_value,
        "ttl": ttl,
        "mx": mx,
    };

    var url = "/cert/modify_record/";

    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: msg,
        success: function (data) {
            $('body').waitMe('hide');
            if (data === "success") {
                swal({
                    // text: old_sub_domain + " 已修改",
                    icon: "success",
                    button: true
                })
                    .then((value) => {
                        // 重载页面
                        window.location.reload()
                    });

            } else {
                swal({
                    text: "修改记录失败: " + old_sub_domain,
                    icon: "error",
                    button: true
                });
            }
        },
        error: function (data, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("修改记录 " + "\n" + textStatus + "\n" + errorThrown);
        }
    })
}


function delete_record(label) {
    var tds = $(label).parent().parent();
    var sub_domain = tds.find("td:nth-child(1)").text();
    var top_domain = $("#top_domain").text();
    var dns_company = $("#dns_company").text();

    var msg = {
        "top_domain": top_domain,
        "dns_company": dns_company,
        "sub_domain": sub_domain,
    };

    var url = "/cert/delete_record/";
    swal({
        title: "Are you sure?",
        text: "删除 " + sub_domain + " ?",
        buttons: true,
        dangerMode: true,
    })
        .then((willDelete) => {
            if (willDelete) {
                run_waitMe("Please wait...");
                $.ajax({
                    url: url,
                    type: "POST",
                    dataType: "json",
                    data: msg,
                    success: function (data) {
                        $('body').waitMe('hide');
                        if (data === "success") {
                            swal({
                                text: sub_domain + " 已删除",
                                icon: "success",
                                button: true
                            })
                                .then((value) => {
                                    // 重载页面
                                    location.reload(true);
                                });
                        } else {
                            swal({
                                text: sub_domain + " 删除失败",
                                icon: "error",
                                button: true
                            });
                        }
                    },
                    error: function (data, textStatus, errorThrown) {
                        $('body').waitMe('hide');
                        alert("删除记录 " + textStatus + " : " + errorThrown);
                    }
                });
            }
        });
}


function set_record_status(label) {
    run_waitMe("Please wait...");

    var tds = $(label).parent().parent();
    var sub_domain = tds.find("td:nth-child(1)").text();
    var top_domain = $("#top_domain").text();
    var dns_company = $("#dns_company").text();

    var td_status = $.trim(tds.find("td:nth-child(6)").text());
    console.log(td_status);

    if (td_status === "正常") {
        var status = "disable";
        var zh_status = "暂停";
    } else {
        var status = "enable";
        var zh_status = "启用";
    }

    var msg = {
        "top_domain": top_domain,
        "dns_company": dns_company,
        "sub_domain": sub_domain,
        "status": status,
    };
    console.log(msg);

    var url = "/cert/set_record_status/";
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: msg,
        success: function (data) {
            $('body').waitMe('hide');
            if (data === "success") {
                swal({
                    text: "已" + zh_status,
                    icon: "success",
                    button: true
                })
                    .then((value) => {
                        // 重载页面
                        window.location.reload()
                    });

            } else {
                swal({
                    text: "修改记录状态失败: " + sub_domain,
                    icon: "error",
                    button: true
                });
            }
        },
        error: function (data, textStatus, errorThrown) {
            $('body').waitMe('hide');
            alert("设置记录状态 " + textStatus + " : " + errorThrown);
        }
    })

}