window.parseISOString = function parseISOString(s) {
    var b = s.split(/\D+/);
    return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
  };
  
  
  const deleteBtns = document.querySelectorAll('.delete-button');
            for (let i = 0; i < deleteBtns.length; i++) {
                const btn = deleteBtns[i];
                console.log('test1')
                btn.onclick = function(e) {
                  console.log('test2')
                  const venueId = e.target.dataset['id'];
                  fetch('/venues/' + venueId, {
                  method: 'DELETE'
                })
                }
            }
  
  