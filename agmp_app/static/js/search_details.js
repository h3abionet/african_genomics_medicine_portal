$(document).ready(function () {
  // initialize data table for detail items
  $('#detail-table, #snps-drugs, #star-alleles-drugs').DataTable({
    dom: 'Bfrtip',
    buttons: [
      'copy', 'csv', 'excel', 'print'
    ]    
  });
});