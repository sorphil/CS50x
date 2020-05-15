 function blink()
            {
                let body = document.querySelector('.ads');
                if (body.style.visibility === 'hidden')
                {
                    body.style.visibility = 'visible'
                }
                else
                {
                    body.style.visibility = 'hidden'
                }
            }
            window.setInterval(blink, 50)