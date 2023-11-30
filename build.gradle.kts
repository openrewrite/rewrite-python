plugins {
    id("org.openrewrite.build.recipe-library") version "latest.integration"
    id("org.openrewrite.build.shadow") version "latest.integration"
    id("nebula.release") version "17.1.0"
}
group = "org.openrewrite"
description = "Rewrite Python"

task("printIntellijDependencies", JavaExec::class) {
    mainClass.set("org.openrewrite.python.internal.CollectIntelliJDependenciesAsm")
    classpath = sourceSets["main"].runtimeClasspath
}

configurations {
    all {
        resolutionStrategy {
            cacheChangingModulesFor(1, TimeUnit.HOURS)
            cacheDynamicVersionsFor(1, TimeUnit.HOURS)
            exclude("ch.qos.logback")
        }
    }
}

val latest = if (project.hasProperty("releasing")) {
    "latest.release"
} else {
    "latest.integration"
}

val lib = fileTree("lib")
dependencies {
    compileOnly("org.openrewrite:rewrite-test")

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")
    implementation(lib)

    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.7.10")
    implementation("io.micrometer:micrometer-core:1.9.+")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.7.3")
    runtimeOnly("org.jetbrains.kotlinx:kotlinx-collections-immutable:0.3.6")
    runtimeOnly("it.unimi.dsi:fastutil:8.5.2")
    runtimeOnly("com.google.guava:guava:31.1-jre")
    runtimeOnly("one.util:streamex:0.8.1")

    implementation("org.ow2.asm:asm:9.5")

    testImplementation("org.assertj:assertj-core:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-api:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-params:latest.release")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")
    testImplementation("org.openrewrite:rewrite-test")

    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:latest.release")
}

repositories {
    mavenLocal()
    maven {
        url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
    }
    mavenCentral()
}

val shadowJar = tasks.named<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar>("shadowJar") {
    from(lib)
    dependencies {
        include { _ -> false }
    }
}

tasks.withType<Javadoc> {
    options {
        this as CoreJavadocOptions
        addStringOption("Xdoclint:none", "-quiet")
    }
}
