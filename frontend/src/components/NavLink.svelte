<script>
    import { page } from '$app/stores';
    export let title;
    export let href;
  </script>
  
  <a class:active="{$page.url.pathname == href}" href={href}>{title}</a>
  <style>

a {
    display: block;
    color: white;
    text-align: center;
    padding: 14px 16px;
    text-decoration: none;
  }
  
a:hover:not(.active) {
    background-color: #111;
  }
.active {
    background-color: #04AA6D;
  }
  </style>
  