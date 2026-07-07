class Footer extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.innerHTML = `
    <style>
        footer {
          padding: 50px 0px 0px 0px
          background: #000000;
      }
      
      footer .social li {
          display: inline;
          margin-left: 20px
      }
      
      footer .social li a {
          font-size: 1.25em;
          color: #999
      }

        footer .social li a i.fa {
          font-family: FontAwesome !important;
          font-style: normal;
          font-weight: normal;
          line-height: 1;
          display: inline-block;
        }

          footer .social li a img[alt="whapp"] {
            width: 18px;
            height: 18px;
            display: inline-block;
            object-fit: contain;
            vertical-align: -2px;
          }

    </style>
    <footer>
		<div class="container">
			<div class="units-row">
			    <div class="unit-50">
          <ul class="social list-flat right">
            <li><a href="my-contacts.html">Contacto</a></li>
            <!--li><a href="https://api.whatsapp.com/send?phone=543547595620" target="_blank" class="foot-phone"-->
            <!--strong> <img src="https://img.icons8.com/external-those-icons-flat-those-icons/24/000000/external-WhatsApp-Logo-social-media-those-icons-flat-those-icons.png"/> </strong> </a></li-->
          </ul>
			    </div>
			    <div class="unit-50">
          <ul class="social list-flat right">
            <li>
              <a href="mailto:sofia_fuentes_24@outlook.es" title="Enviar email" aria-label="Email">
                <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v.217L8 8.583.001 4.217V4z"/>
                  <path d="M0 5.383V12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5.383l-7.4 4.933a1 1 0 0 1-1.2 0L0 5.383z"/>
                </svg>
              </a>
            </li>
						<li><a href="https://www.instagram.com/sofifuentesx?igsh=MXR3OHJsN2lubDAyZQ=="  target="_blank"><i class="fa fa-instagram"></i></a></li>
            <li><a href="https://api.whatsapp.com/send?phone=543547595620"  target="_blank"><img src="../static/img/whatsapp-logo3.png" alt="whapp"></a></li>
					</ul>
			    </div>
			</div>
		</div>
	</footer>
      `;
  }
}

customElements.define('footer-component', Footer)