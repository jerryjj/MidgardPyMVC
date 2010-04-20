<%inherit file="/base/default.mako" />

<%def name="body()">

${ h.form(url(controller='login', action='doLogin', came_from=c.came_from, __logins=c.login_counter), method='POST', multipart=False) }
  <label for="login">${ _("Username") }:</label><input type="text" id="login" name="login" /><br/>
  <label for="password">${ _("Password") }:</label><input type="password" id="password" name="password" />
  <input type="submit" value="Login" />
</form>

</%def>