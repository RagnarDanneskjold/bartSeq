from configparser import RawConfigParser
from dataclasses import dataclass
from typing import TextIO


@dataclass
class PsConfiguration:
    max_threads: int
    p3_path: str
    p3_config_path: str
    p3_thermo_path: str
    blast_path: str
    blast_dbpath: str
    blast_dbname: str
    blast_max_hits: int
    rnacf_path: str
    opt_steps: int
    opt_max_temp: int

    @staticmethod
    def write_standard_config(path):  # Write the standard settings file
        """ Write the standard settings file
        """
        config = RawConfigParser()
        config.set("DEFAULT", "threads", "1")

        config.add_section("Primer3")
        config.set("Primer3", "path", "/usr/local/bin/primer3_core")
        config.set("Primer3", "configPath", "")
        config.set("Primer3", "thermoParamPath", "")

        config.add_section("BLAST")
        config.set("BLAST", "path", "")
        config.set("BLAST", "db_path", "")
        config.set("BLAST", "db_name", "")
        config.set("BLAST", "maxHits", 5)

        config.add_section("RNAcofold")
        config.set("RNAcofold", "path", "")

        config.add_section("Optimization")
        config.set("Optimization", "steps", 500)
        config.set("Optimization", "maxTemp", 15)

        with open(path, "w") as configfile:
            config.write(configfile)

    @staticmethod
    def read_config(handle: TextIO) -> "PsConfiguration":  # Read the settings file
        """ Read the settings file
        """
        config = RawConfigParser()
        config.read_file(handle)
        return PsConfiguration(
            max_threads=config.getint("DEFAULT", "threads"),
            p3_path=config.get("Primer3", "path"),
            p3_config_path=config.get("Primer3", "configPath"),
            p3_thermo_path=config.get("Primer3", "thermoParamPath"),
            blast_path=config.get("BLAST", "path"),
            blast_dbpath=config.get("BLAST", "db_path"),
            blast_dbname=config.get("BLAST", "db_name"),
            blast_max_hits=config.getint("BLAST", "maxHits"),
            rnacf_path=config.get("RNAcofold", "path"),
            opt_steps=config.getint("Optimization", "steps"),
            opt_max_temp=config.getint("Optimization", "maxTemp"),
        )
