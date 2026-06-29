"""
Auth Service Provider
=====================

Define authorization gates and register model policies.
Gates provide a closure-based approach to authorization, while policies
organize authorization logic around a particular model or resource.
"""

from laraflask.core.providers import ServiceProvider


class AuthServiceProvider(ServiceProvider):
    """
    Register authentication and authorization services.

    This provider is responsible for registering model policies and
    defining gate abilities that control access throughout the application.
    """

    # -------------------------------------------------------------------------
    # Policy Mappings
    # -------------------------------------------------------------------------
    # Map model class paths to their corresponding policy class paths.
    # Policies are classes that organize authorization logic around a model.
    # Each policy class should define methods like view(), create(), update(),
    # delete(), restore(), and forceDelete().
    #
    # Example:
    #   policies = {
    #       'app.Models.Post.Post': 'app.Policies.PostPolicy.PostPolicy',
    #       'app.Models.Comment.Comment': 'app.Policies.CommentPolicy.CommentPolicy',
    #       'app.Models.Project.Project': 'app.Policies.ProjectPolicy.ProjectPolicy',
    #   }

    policies = {}

    def register(self):
        """Register any authentication / authorization services."""
        pass

    def boot(self):
        """
        Register policies and define gate abilities.

        Gates are evaluated in the order they are defined. A gate that
        returns a non-None value will short-circuit further checks.
        """
        from laraflask.auth.auth import Gate

        # Register model policies from the policies dict
        self.register_policies()

        # -----------------------------------------------------------------
        # Before Hook (Super-Admin Bypass)
        # -----------------------------------------------------------------
        # The before() callback runs prior to all other authorization checks.
        # Returning True grants all abilities; returning None falls through
        # to the specific gate/policy check.
        #
        # Gate.before(lambda user, ability: True if user.is_super_admin else None)

        # -----------------------------------------------------------------
        # Gate Definitions
        # -----------------------------------------------------------------
        # Define simple closure-based authorization checks. Use gates for
        # actions that are not tied to a specific model instance.

        # Admin role check
        # Gate.define('admin', lambda user: user.role == 'admin')

        # Moderator or higher check
        # Gate.define('moderator', lambda user: user.role in ['admin', 'moderator'])

        # Resource ownership check (for actions tied to a resource)
        # Gate.define('update-post', lambda user, post: post.user_id == user.id)

        # Team membership check
        # Gate.define('belongs-to-team', lambda user, team:
        #     team.members.contains(user.id)
        # )

        # Feature flag / subscription-based gate
        # Gate.define('access-premium', lambda user:
        #     user.subscription and user.subscription.is_active()
        # )

        # -----------------------------------------------------------------
        # After Hook
        # -----------------------------------------------------------------
        # The after() callback runs after the authorization check completes.
        # Useful for logging or auditing authorization decisions.
        #
        # Gate.after(lambda user, ability, result:
        #     log_authorization(user, ability, result)
        # )

    def register_policies(self):
        """
        Register model policies from the policies dict.

        Iterates over the policies mapping and registers each model-policy
        pair with the Gate facade. Handles import errors gracefully to avoid
        breaking the boot sequence if a policy class is missing.
        """
        from laraflask.auth.auth import Gate
        import importlib

        for model_path, policy_path in self.policies.items():
            try:
                # Resolve the model class
                m_module_path, m_class_name = model_path.rsplit('.', 1)
                m_module = importlib.import_module(m_module_path)
                model = getattr(m_module, m_class_name)

                # Resolve the policy class
                p_module_path, p_class_name = policy_path.rsplit('.', 1)
                p_module = importlib.import_module(p_module_path)
                policy = getattr(p_module, p_class_name)

                # Register the policy with the Gate
                Gate.policy(model, policy)
            except (ImportError, AttributeError) as e:
                # Log the error but do not halt boot; the policy may not
                # exist yet during development.
                pass
