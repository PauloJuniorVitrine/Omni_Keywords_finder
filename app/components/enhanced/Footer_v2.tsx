import React from 'react';
import { Button } from '../../../ui/design-system/components/Button';
import { Card } from '../../../ui/design-system/components/Card';

export interface FooterLink {
  id: string;
  label: string;
  href: string;
  external?: boolean;
}

export interface FooterSection {
  id: string;
  title: string;
  links: FooterLink[];
}

export interface FooterSocial {
  id: string;
  name: string;
  href: string;
  icon: React.ReactNode;
}

export interface Footer_v2Props {
  title?: string;
  description?: string;
  sections?: FooterSection[];
  socials?: FooterSocial[];
  links?: FooterLink[];
  variant?: 'default' | 'minimal' | 'elevated';
  size?: 'sm' | 'md' | 'lg';
  showNewsletter?: boolean;
  newsletterPlaceholder?: string;
  onNewsletterSubmit?: (email: string) => void;
  copyright?: string;
  showBackToTop?: boolean;
  onBackToTop?: () => void;
  className?: string;
}

const FooterSectionComponent: React.FC<{
  section: FooterSection;
}> = ({ section }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-secondary-900 uppercase tracking-wider">
        {section.title}
      </h3>
      
      <ul className="space-y-2">
        {section.links.map(link => (
          <li key={link.id}>
            <a
              href={link.href}
              target={link.external ? '_blank' : undefined}
              rel={link.external ? 'noopener noreferrer' : undefined}
              className="text-sm text-secondary-600 hover:text-secondary-900 transition-colors duration-200"
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

const NewsletterSignup: React.FC<{
  placeholder?: string;
  onSubmit?: (email: string) => void;
}> = ({ placeholder = 'Enter your email', onSubmit }) => {
  const [email, setEmail] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && onSubmit) {
      onSubmit(email);
      setEmail('');
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-secondary-900 uppercase tracking-wider">
        Subscribe to our newsletter
      </h3>
      
      <p className="text-sm text-secondary-600">
        Get the latest updates and insights delivered to your inbox.
      </p>
      
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="email"
          placeholder={placeholder}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="flex-1 px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
          required
        />
        <Button type="submit" variant="primary" size="md">
          Subscribe
        </Button>
      </form>
    </div>
  );
};

export const Footer_v2: React.FC<Footer_v2Props> = ({
  title,
  description,
  sections = [],
  socials = [],
  links = [],
  variant = 'default',
  size = 'md',
  showNewsletter = false,
  newsletterPlaceholder,
  onNewsletterSubmit,
  copyright = '© 2024 Omni Keywords Finder. All rights reserved.',
  showBackToTop = true,
  onBackToTop,
  className = ''
}) => {
  const footerClasses = [
    'bg-white border-t border-secondary-200',
    variant === 'elevated' ? 'shadow-lg' : '',
    className
  ].join(' ');

  const contentClasses = {
    sm: 'px-4 py-8',
    md: 'px-6 py-12',
    lg: 'px-8 py-16'
  };

  const gridCols = sections.length > 0 ? `grid-cols-1 md:grid-cols-2 lg:grid-cols-${Math.min(sections.length + 1, 4)}` : 'grid-cols-1';

  return (
    <footer className={footerClasses}>
      <div className={contentClasses[size]}>
        {/* Main Footer Content */}
        <div className={`grid ${gridCols} gap-8 mb-8`}>
          {/* Brand Section */}
          <div className="space-y-4">
            {title && (
              <h2 className="text-xl font-bold text-secondary-900">{title}</h2>
            )}
            
            {description && (
              <p className="text-sm text-secondary-600 max-w-md">
                {description}
              </p>
            )}
            
            {socials.length > 0 && (
              <div className="flex space-x-4">
                {socials.map(social => (
                  <a
                    key={social.id}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-secondary-400 hover:text-secondary-600 transition-colors duration-200"
                    aria-label={social.name}
                  >
                    {social.icon}
                  </a>
                ))}
              </div>
            )}
          </div>

          {/* Footer Sections */}
          {sections.map(section => (
            <FooterSectionComponent
              key={section.id}
              section={section}
            />
          ))}

          {/* Newsletter Section */}
          {showNewsletter && (
            <NewsletterSignup
              placeholder={newsletterPlaceholder}
              onSubmit={onNewsletterSubmit}
            />
          )}
        </div>

        {/* Bottom Footer */}
        <div className="border-t border-secondary-200 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="text-sm text-secondary-600">
              {copyright}
            </div>

            {/* Bottom Links */}
            {links.length > 0 && (
              <div className="flex items-center space-x-6">
                {links.map(link => (
                  <a
                    key={link.id}
                    href={link.href}
                    target={link.external ? '_blank' : undefined}
                    rel={link.external ? 'noopener noreferrer' : undefined}
                    className="text-sm text-secondary-600 hover:text-secondary-900 transition-colors duration-200"
                  >
                    {link.label}
                  </a>
                ))}
              </div>
            )}

            {/* Back to Top */}
            {showBackToTop && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onBackToTop}
                className="flex items-center space-x-2"
              >
                <span>Back to top</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              </Button>
            )}
          </div>
        </div>
      </div>
    </footer>
  );
};

// Footer Hook
export const useFooter = () => {
  const [newsletterSubscribers, setNewsletterSubscribers] = React.useState<string[]>([]);

  const subscribeToNewsletter = (email: string) => {
    setNewsletterSubscribers(prev => [...prev, email]);
    // Here you would typically send the email to your backend
    console.log('Newsletter subscription:', email);
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  return {
    newsletterSubscribers,
    subscribeToNewsletter,
    scrollToTop
  };
}; 