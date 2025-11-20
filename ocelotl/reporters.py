"""
Ocelotl v3.0 - Generadores de Reportes
Sistema para generar reportes en JSON y HTML
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .utils import Colors


class ReportGenerator:
    """Generador de reportes en múltiples formatos"""
    
    def __init__(self, results: Dict[str, Any], colors: Colors):
        self.results = results
        self.colors = colors
    
    def generate_json_report(self, output_file: str) -> bool:
        """
        Genera reporte en formato JSON
        
        Args:
            output_file: Ruta del archivo de salida
            
        Returns:
            bool: True si se generó exitosamente
        """
        try:
            report = {
                'metadata': {
                    'tool': 'Ocelotl',
                    'version': '3.0',
                    'scan_time': self.results['stats'].get('start_time'),
                    'end_time': self.results['stats'].get('end_time'),
                    'duration': self._calculate_duration()
                },
                'summary': self.results['stats'],
                'findings': {
                    'admin_credentials': self.results.get('admin_credentials', []),
                    'passwords': self.results.get('passwords', []),
                    'credentials': self.results.get('credentials', []),
                    'api_keys': self.results.get('api_keys', []),
                    'private_keys': self.results.get('private_keys', []),
                    'jwt_tokens': self.results.get('jwt_tokens', []),
                    'config_files': self.results.get('config_files', []),
                    'sensitive_files': self.results.get('sensitive_files', [])
                },
                'statistics': self._generate_statistics()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error generating JSON report: {e}")
            return False
    
    def generate_html_report(self, output_file: str = 'ocelotl_report.html') -> bool:
        """
        Genera reporte en formato HTML interactivo
        
        Args:
            output_file: Ruta del archivo de salida
            
        Returns:
            bool: True si se generó exitosamente
        """
        try:
            html_content = self._build_html()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return False
    
    def _calculate_duration(self) -> str:
        """Calcula la duración del escaneo"""
        try:
            start = datetime.fromisoformat(self.results['stats'].get('start_time', ''))
            end = datetime.fromisoformat(self.results['stats'].get('end_time', datetime.now().isoformat()))
            duration = end - start
            return str(duration).split('.')[0]
        except:
            return "Unknown"
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """Genera estadísticas del escaneo"""
        stats = {
            'by_type': {},
            'by_confidence': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'VERY_LOW': 0
            },
            'false_positives_filtered': 0,
            'total_findings': 0
        }
        
        # Contar por tipo
        for key in ['admin_credentials', 'passwords', 'credentials', 'api_keys', 
                   'private_keys', 'jwt_tokens', 'config_files', 'sensitive_files']:
            count = len(self.results.get(key, []))
            stats['by_type'][key] = count
            stats['total_findings'] += count
        
        # Contar por nivel de confianza
        for key in ['admin_credentials', 'passwords', 'credentials', 'api_keys']:
            for item in self.results.get(key, []):
                validation = item.get('validation', {})
                confidence = validation.get('confidence', 'VERY_LOW')
                stats['by_confidence'][confidence] += 1
                
                if validation.get('is_likely_false_positive', False):
                    stats['false_positives_filtered'] += 1
        
        return stats
    
    def _build_html(self) -> str:
        """Construye el contenido HTML del reporte"""
        stats = self._generate_statistics()
        duration = self._calculate_duration()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ocelotl Security Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card.critical {{ border-color: #dc3545; }}
        .stat-card.high {{ border-color: #fd7e14; }}
        .stat-card.medium {{ border-color: #ffc107; }}
        .stat-card.low {{ border-color: #17a2b8; }}
        .stat-card.info {{ border-color: #6c757d; }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .findings-section {{
            padding: 30px;
        }}
        
        .finding-category {{
            margin-bottom: 30px;
        }}
        
        .category-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px 8px 0 0;
            font-size: 1.3em;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .category-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        
        .finding-item {{
            background: #f8f9fa;
            padding: 20px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #6c757d;
        }}
        
        .finding-item.critical {{ border-color: #dc3545; background: #fff5f5; }}
        .finding-item.high {{ border-color: #fd7e14; background: #fff8f0; }}
        .finding-item.medium {{ border-color: #ffc107; background: #fffbf0; }}
        .finding-item.low {{ border-color: #17a2b8; background: #f0f9fc; }}
        
        .finding-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            align-items: center;
        }}
        
        .finding-file {{
            font-family: 'Courier New', monospace;
            color: #495057;
            font-weight: bold;
        }}
        
        .confidence-badge {{
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .confidence-critical {{ background: #dc3545; color: white; }}
        .confidence-high {{ background: #fd7e14; color: white; }}
        .confidence-medium {{ background: #ffc107; color: black; }}
        .confidence-low {{ background: #17a2b8; color: white; }}
        .confidence-very-low {{ background: #6c757d; color: white; }}
        
        .finding-details {{
            font-family: 'Courier New', monospace;
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            overflow-x: auto;
            font-size: 0.9em;
        }}
        
        .finding-context {{
            color: #6c757d;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        
        .footer {{
            background: #343a40;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .no-findings {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }}
        
        .chart {{
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .stat-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐆 OCELOTL</h1>
            <p class="subtitle">Security Scan Report</p>
            <p style="margin-top: 15px; opacity: 0.8;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Duration: {duration}
            </p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card critical">
                <div class="stat-label">Critical Findings</div>
                <div class="stat-value">{stats['by_confidence']['CRITICAL']}</div>
            </div>
            <div class="stat-card high">
                <div class="stat-label">High Confidence</div>
                <div class="stat-value">{stats['by_confidence']['HIGH']}</div>
            </div>
            <div class="stat-card medium">
                <div class="stat-label">Medium Confidence</div>
                <div class="stat-value">{stats['by_confidence']['MEDIUM']}</div>
            </div>
            <div class="stat-card low">
                <div class="stat-label">Total Findings</div>
                <div class="stat-value">{stats['total_findings']}</div>
            </div>
            <div class="stat-card info">
                <div class="stat-label">Files Scanned</div>
                <div class="stat-value">{self.results['stats'].get('files_scanned', 0)}</div>
            </div>
            <div class="stat-card info">
                <div class="stat-label">False Positives</div>
                <div class="stat-value">{stats['false_positives_filtered']}</div>
            </div>
        </div>
        
        <div class="findings-section">
            {self._generate_findings_html()}
        </div>
        
        <div class="footer">
            <p><strong>Ocelotl v3.0</strong> - Advanced Security Scanner</p>
            <p style="margin-top: 10px; opacity: 0.7;">
                ⚠️ For authorized security audits only | github.com/Kon3e/Ocelotl
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_findings_html(self) -> str:
        """Genera el HTML de los hallazgos"""
        categories = {
            'admin_credentials': ('Admin Credentials', '👤'),
            'passwords': ('Passwords', '🔑'),
            'api_keys': ('API Keys & Tokens', '🎫'),
            'credentials': ('Database Credentials', '🗄️'),
            'private_keys': ('Private Keys', '🔐'),
            'jwt_tokens': ('JWT Tokens', '🎟️'),
            'sensitive_files': ('Sensitive Files', '📄')
        }
        
        html_parts = []
        
        for category_key, (category_name, emoji) in categories.items():
            findings = self.results.get(category_key, [])
            
            if not findings:
                continue
            
            html_parts.append(f"""
            <div class="finding-category">
                <div class="category-header">
                    <span>{emoji} {category_name}</span>
                    <span class="category-badge">{len(findings)} found</span>
                </div>
            """)
            
            for finding in findings[:50]:  # Limitar a 50 por categoría
                confidence = finding.get('validation', {}).get('confidence', 'VERY_LOW').lower().replace('_', '-')
                confidence_display = finding.get('validation', {}).get('confidence', 'VERY_LOW')
                
                file_path = finding.get('file', 'Unknown')
                line = finding.get('line', 0)
                match = finding.get('match', '')
                context = finding.get('context', '')
                
                # Sanitizar HTML
                match = match.replace('<', '&lt;').replace('>', '&gt;')
                context = context.replace('<', '&lt;').replace('>', '&gt;')
                
                html_parts.append(f"""
                <div class="finding-item {confidence}">
                    <div class="finding-header">
                        <div class="finding-file">📁 {file_path}:{line}</div>
                        <span class="confidence-badge confidence-{confidence}">{confidence_display}</span>
                    </div>
                    <div class="finding-details">
                        {match[:200]}
                    </div>
                    <div class="finding-context">
                        Context: {context[:300]}...
                    </div>
                </div>
                """)
            
            if len(findings) > 50:
                html_parts.append(f"""
                <div class="no-findings">
                    ... and {len(findings) - 50} more findings (check JSON report for complete list)
                </div>
                """)
            
            html_parts.append("</div>")
        
        if not html_parts:
            return '<div class="no-findings"><h2>✅ No critical findings detected!</h2></div>'
        
        return ''.join(html_parts)
    
    def print_summary(self):
        """Imprime resumen en consola"""
        stats = self._generate_statistics()
        duration = self._calculate_duration()
        
        c = self.colors
        
        print(f"\n{c.CYAN}{'=' * 80}{c.RESET}")
        print(f"{c.BOLD}{c.CYAN}                        SCAN SUMMARY{c.RESET}")
        print(f"{c.CYAN}{'=' * 80}{c.RESET}\n")
        
        print(f"{c.BLUE}[+] Duration:{c.RESET} {duration}")
        print(f"{c.BLUE}[+] Files Scanned:{c.RESET} {self.results['stats'].get('files_scanned', 0)}")
        print(f"{c.BLUE}[+] Total Matches:{c.RESET} {self.results['stats'].get('matches_found', 0)}")
        print(f"{c.BLUE}[+] Errors:{c.RESET} {self.results['stats'].get('errors', 0)}")
        
        print(f"\n{c.YELLOW}{c.BOLD}FINDINGS BY CONFIDENCE:{c.RESET}")
        print(f"{c.RED}  [!] CRITICAL:{c.RESET} {stats['by_confidence']['CRITICAL']}")
        print(f"{c.MAGENTA}  [*] HIGH:{c.RESET}     {stats['by_confidence']['HIGH']}")
        print(f"{c.YELLOW}  [!] MEDIUM:{c.RESET}   {stats['by_confidence']['MEDIUM']}")
        print(f"{c.BLUE}  [i] LOW:{c.RESET}      {stats['by_confidence']['LOW']}")
        print(f"{c.WHITE}  [.] VERY_LOW:{c.RESET} {stats['by_confidence']['VERY_LOW']}")
        
        print(f"\n{c.YELLOW}{c.BOLD}FINDINGS BY TYPE:{c.RESET}")
        type_labels = {
            'admin_credentials': ('[ADMIN] Admin Credentials', 'RED'),
            'passwords': ('[PASS] Passwords', 'RED'),
            'api_keys': ('[API] API Keys/Tokens', 'MAGENTA'),
            'credentials': ('[DB] DB Credentials', 'YELLOW'),
            'private_keys': ('[KEY] Private Keys', 'RED'),
            'jwt_tokens': ('[JWT] JWT Tokens', 'MAGENTA'),
            'config_files': ('[CFG] Config Files', 'BLUE'),
            'sensitive_files': ('[FILE] Sensitive Files', 'YELLOW')
        }
        
        for key, (label, color) in type_labels.items():
            count = stats['by_type'].get(key, 0)
            color_code = getattr(c, color)
            print(f"{color_code}  {label}:{c.RESET} {count}")
        
        print(f"\n{c.CYAN}{'=' * 80}{c.RESET}\n")
