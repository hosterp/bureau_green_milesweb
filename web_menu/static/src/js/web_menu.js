openerp.web_menu = function(instance){
    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    instance.web.Menu =  instance.web.Widget.extend({
        init: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.has_been_loaded = $.Deferred();
            this.is_bound = $.Deferred();
            this.click_on_main_menu = false
            this.maximum_visible_links = 'auto'; // # of menu to show. 0 = do not crop, 'auto' = algo
            this.data = {data:{children:[]}};
            if (window.localStorage) {
                this.folded = localStorage.getItem('oe_menu_folded') === 'true';
            }
            this.on("menu_bound", this, function (menu_data) {
                self.reflow();
                var $all_menus = self.$el.parents('body').find('.oe_webclient').find('[data-menu]');
                var all_menu_ids = _.map($all_menus, function (menu) {return parseInt($(menu).attr('data-menu'), 10);});
                if (!_.isEmpty(all_menu_ids)) {
                    this.do_load_needaction(all_menu_ids);
                }
            });
        },
        start: function() {
            this._super.apply(this, arguments);
            return this.bind_menu();
        },
        do_reload: function() {
            var self = this;
            self.bind_menu();
        },
        bind_menu: function() {
            var self = this;
            this.$secondary_menus = this.$el.parents().find('.oe_secondary_menus_container')
            this.$secondary_menus.addClass(this.folded ? 'oe_folded' : 'oe_unfolded');
            this.$secondary_menus.on('click', 'a[data-menu]', this.on_menu_click);
            this.$el.parents().find(".oe_toggle_secondary_menu").on('click',this.on_toggle_fold);
            this.$el.on('click', 'a[data-menu]', this.on_top_menu_click);
            $(".oe_menu_unfold").hide()
            $(document).click(function(e) {
                if(! $(e.target).hasClass("oe_menu_text") &&  !$(e.target).hasClass("oe_menu_toggler") &&  !$(e.target).hasClass("oe_secondary_submenu")
                        &&  !$(e.target).hasClass("oe_secondary_menu_section") &&  !$(e.target).hasClass("oe_secondary_menu") && self.folded){
                  self.$secondary_menus.hide();
                }
            });

            // Hide second level submenus
            this.$secondary_menus.find('.oe_menu_toggler').siblings('.oe_secondary_submenu').hide();
            if (self.current_menu) {
                self.open_menu(self.current_menu);
            }
            this.trigger('menu_bound');

            var lazyreflow = _.debounce(this.reflow.bind(this), 200);
            instance.web.bus.on('resize', this, function() {
                if (parseInt(self.$el.parent().css('width')) <= 768 ) {
                    lazyreflow('all_outside');
                } else {
                    lazyreflow();
                }
            });
            instance.web.bus.trigger('resize');

            this.is_bound.resolve();
        },
        do_load_needaction: function (menu_ids) {
            var self = this;
            menu_ids = _.compact(menu_ids);
            if (_.isEmpty(menu_ids)) {
                return $.when();
            }
            return this.rpc("/web/menu/load_needaction", {'menu_ids': menu_ids}).done(function(r) {
                self.on_needaction_loaded(r);
            });
        },
        on_needaction_loaded: function(data) {
            var self = this;
            this.needaction_data = data;
            _.each(this.needaction_data, function (item, menu_id) {
                var $item = self.$secondary_menus.find('a[data-menu="' + menu_id + '"]');
                $item.find('.badge').remove();
                if (item.needaction_counter && item.needaction_counter > 0) {
                    $item.append(QWeb.render("Menu.needaction_counter", { widget : item }));
                }
            });
        },
        /**
         * Reflow the menu items and dock overflowing items into a "More" menu item.
         * Automatically called when 'menu_bound' event is triggered and on window resizing.
         *
         * @param {string} behavior If set to 'all_outside', all the items are displayed. If set to
         * 'all_inside', all the items are hidden under the more item. If not set, only the
         * overflowing items are hidden.
         */
        reflow: function(behavior) {
            var self = this;
            var $more_container = this.$('#menu_more_container').hide();
            var $more = this.$('#menu_more');
            var $systray = this.$el.parents().find('.oe_systray');

            $more.children('li').insertBefore($more_container);  // Pull all the items out of the more menu

            // 'all_outside' beahavior should display all the items, so hide the more menu and exit
            if (behavior === 'all_outside') {
                this.$el.find('li').show();
                $more_container.hide();
                return;
            }

            var $toplevel_items = this.$el.find('li').not($more_container).not($systray.find('li')).hide();
            $toplevel_items.each(function() {
                // In all inside mode, we do not compute to know if we must hide the items, we hide them all
                if (behavior === 'all_inside') {
                    return false;
                }
                var remaining_space = self.$el.parent().width() - $more_container.outerWidth();
                self.$el.parent().children(':visible').each(function() {
                    remaining_space -= $(this).outerWidth();
                });

                if ($(this).width() > remaining_space) {
                    return false;
                }
                $(this).show();
            });
            $more.append($toplevel_items.filter(':hidden').show());
            $more_container.toggle(!!$more.children().length || behavior === 'all_inside');
            // Hide toplevel item if there is only one
            var $toplevel = this.$el.children("li:visible");
            if ($toplevel.length === 1 && behavior != 'all_inside') {
                $toplevel.hide();
            }
        },
        on_toggle_fold: function(e) {
            this.$secondary_menus.toggleClass('oe_folded').toggleClass('oe_unfolded');
            $(".oe_secondary_submenu").find('.active a').click();
            if ( $(".oe_toggle_secondary_menu .oe_menu_fold").css("display") == 'none') {
                this.folded = true
                this.$secondary_menus.find('.oe_secondary_menu.active_menu').show();
                $('.oe_logo').show();
                $(".oe_leftbar").show()
                $(".oe_menu_fold").show()
                $(".oe_menu_unfold").hide()
                this.$secondary_menus.css("display","block")
                this.$secondary_menus.removeClass("active_menu")
                this.$secondary_menus.css("margin-left",0)
                this.$secondary_menus.removeClass("active_menu")
                $(this.$secondary_menus.parents('.oe_leftbar > div')[0]).removeClass("set_width")
            } else {
                this.folded = false
                this.$secondary_menus.find('.oe_secondary_menu').hide();
                $('.oe_logo').hide();
                $(".oe_leftbar").hide()
                $(".oe_menu_fold").hide()
                $(".oe_menu_unfold").show()
            }
            this.folded = !this.folded;
            if (window.localStorage) {
                localStorage.setItem('oe_menu_folded', this.folded.toString());
            }
        },
        /**
         * Opens a given menu by id, as if a user had browsed to that menu by hand
         * except does not trigger any event on the way
         *
         * @param {Number} id database id of the terminal menu to select
         */
        open_menu: function (id) {
            this.current_menu = id;
            this.session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            this.$el.add(this.$secondary_menus).find('.active_menu')
                .removeClass('active');
            this.$secondary_menus.find('> .oe_secondary_menu').hide();
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']').parent();
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
            }

            if(this.folded){
                var margin_left = $main_menu.position()
                this.$secondary_menus.addClass("active_menu")
                this.$secondary_menus.css("margin-left",margin_left.left)
                this.$secondary_menus.css("display","block")
                this.$secondary_menus.find('.oe_secondary_menu').hide();
                if(this.$secondary_menus.parents('.oe_leftbar').length){
                    $(this.$secondary_menus.parents('.oe_leftbar > div')[0]).addClass("set_width")
                }
                $('.oe_logo').hide();
                $('.oe_footer').hide();
                $(".oe_menu_fold").hide()
                $(".oe_menu_unfold").show()
            }else{
                this.$secondary_menus.css("display","block")
                if(this.$secondary_menus.parents('.oe_leftbar').length){
                    $(this.$secondary_menus.parents('.oe_leftbar > div')[0]).removeClass("set_width")
                }
                this.$secondary_menus.removeClass("active_menu")
                this.$secondary_menus.css("margin-left",0)
                this.$secondary_menus.removeClass("active_menu")
            }

            // Activate current main menu
            this.$el.find('.active').removeClass('active');
            $main_menu.parent().addClass('active');

            // Show current sub menu
            this.$secondary_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Hide/Show the leftbar menu depending of the presence of sub-items
            this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);

            // Activate current menu item and show parents
            this.$secondary_menus.find('.active').removeClass('active');
            if ($main_menu !== $clicked_menu) {
                $clicked_menu.parents().show();
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    if(this.folded && this.click_on_main_menu == false){
                        $(".oe_secondary_menus_container,oe_folded,active_menu").hide()
                    }
                    $clicked_menu.parent().addClass('active');
                }
            }
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'destroy');
           });
        },
        /**
         * Call open_menu with the first menu_item matching an action_id
         *
         * @param {Number} id the action_id to match
         */
        open_action: function (id) {
            var $menu = this.$el.add(this.$secondary_menus).find('a[data-action-id="' + id + '"]');
            var menu_id = $menu.data('menu');
            if (menu_id) {
                this.open_menu(menu_id);
            }
        },

        /**
         * Process a click on a menu item
         *
         * @param {Number} id the menu_id
         * @param {Boolean} [needaction=false] whether the triggered action should execute in a `needs action` context
         */
        menu_click: function(id, needaction) {
            if (!id) { return; }

            // find back the menuitem in dom to get the action
            var $item = this.$el.find('a[data-menu=' + id + ']');
            if (!$item.length) {
                $item = this.$secondary_menus.find('a[data-menu=' + id + ']');
            }
            var action_id = $item.data('action-id');
            // If first level menu doesnt have action trigger first leaf
            if (!action_id) {
                if(this.$el.has($item).length) {
                    var $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + id + ']');
                    var $items = $sub_menu.find('a[data-action-id]').filter('[data-action-id!=""]');
                    if($items.length) {
                        action_id = $items.data('action-id');
                        id = $items.data('menu');
                    }
                }
            }
            if (action_id) {
                if(this.folded){
                    $(".oe_secondary_menus_container").hide()
                    $(".oe_leftbar").hide()
                    $(".active_menu").hide()
                }else{
                    $(".oe_secondary_menus_container").show()
                }
                if(! this.click_on_main_menu){
                    this.trigger('menu_click', {
                        action_id: action_id,
                        needaction: needaction,
                        id: id,
                        previous_menu_id: this.current_menu // Here we don't know if action will fail (in which case we have to revert menu)
                    }, $item);
                }
            } else {
                console.log('Menu no action found web test 04 will fail');
            }
            this.open_menu(id);
        },
        do_reload_needaction: function () {
            var self = this;
            if (self.current_menu) {
                self.do_load_needaction([self.current_menu]).then(function () {
                    self.trigger("need_action_reloaded");
                });
            }
        },
        /**
         * Jquery event handler for menu click
         *
         * @param {Event} ev the jquery event
         */
        on_top_menu_click: function(ev) {
            ev.preventDefault();
            var self = this;
            var id = $(ev.currentTarget).data('menu');

            // Fetch the menu leaves ids in order to check if they need a 'needaction'
            var $secondary_menu = this.$el.parents().find('.oe_secondary_menu[data-menu-parent=' + id + ']');
            var $menu_leaves = $secondary_menu.children().find('.oe_menu_leaf');
            var menu_ids = _.map($menu_leaves, function (leave) {return parseInt($(leave).attr('data-menu'), 10);});

            self.do_load_needaction(menu_ids).then(function () {
                self.trigger("need_action_reloaded");
            });
            this.$el.parents().find(".oe_secondary_menus_container").scrollTop(0,0);

            this.on_menu_click(ev);
        },
        on_menu_click: function(ev) {
            if($(ev.currentTarget).closest("li").closest("ul").attr("main") && $(ev.currentTarget).attr("main")){
                if ($(".oe_toggle_secondary_menu .oe_menu_fold").css("display") == 'none') {
                    this.click_on_main_menu = true
                }else{
                    this.click_on_main_menu = false
                }
            }else{
                this.click_on_main_menu = false
            }
            ev.preventDefault();
            var needaction = $(ev.target).is('div#menu_counter');
            this.menu_click($(ev.currentTarget).data('menu'), needaction);
        },
    });

}






