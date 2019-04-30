(function ($) {
    'use strict';
    $(function () {
        $('#order-listing')
        // .on('order.dt', function () {
        //     console.log('Order');
        // })
        // .on('search.dt', function () {
        //     console.log('Search');
        // })
            .on('page.dt', function () {
                modify_row_style();
                console.log('next Page');

            }).DataTable({
            "aLengthMenu": [
                // [5, 10, 15, -1],
                // [5, 10, 15, "All"]
                [10, 20, 40, -1],
                [10, 20, 40, "All"]
            ],
            "iDisplayLength": 20,
            "language": {
                search: "",
                // 自定义属性部分
                "lengthMenu": "每页 _MENU_ 条记录",
                "zeroRecords": "没有找到记录",
                "info": "第 _PAGE_ 页 ( 总共 _PAGES_ 页 )",
                "infoEmpty": "无记录",
                "infoFiltered": "(从 _MAX_ 条记录过滤)",
                "oPaginate": {
                    // "sFirst": "首页",
                    "sPrevious": "«",
                    "sNext": "»",
                    // "sLast": "尾页"
                },
                // 自定义属性部分
            },
            "columnDefs": [{
                orderable: false,//禁用排序
                targets: [6, 7]   //指定的列
            }],
        });
        $('#order-listing').each(function () {
            var datatable = $(this);
            // SEARCH - Add the placeholder for Search and Turn this into in-line form control
            var search_input = datatable.closest('.dataTables_wrapper').find('div[id$=_filter] input');
            search_input.attr('placeholder', 'Search');
            search_input.removeClass('form-control-sm');
            // LENGTH - Inline-Form control
            var length_sel = datatable.closest('.dataTables_wrapper').find('div[id$=_length] select');
            length_sel.removeClass('form-control-sm');
        });
    });
})(jQuery);