$(document).ready(function () {
  // initialize data table for detail items
  $('#detail-table').DataTable({
    dom: 'Bfrtip',
    buttons: [
      'copy', 'csv', 'excel', 'print'
    ]    
  });
});